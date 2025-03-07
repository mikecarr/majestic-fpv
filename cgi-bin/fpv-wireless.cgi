#!/usr/bin/haserl
<%in p/common.cgi %>
<% set -x %>
<%
page_title="Wireless Settings"

params="channel power_level mcs_index sdpc ldpc"

wfb_file="/etc/wfb.conf"

# Check if the file exists
if [ ! -f "$wfb_file" ]; then
    echo "Error: Config file not found: $wfb_file"
    exit 1
fi

# Function to map "true" and "false" to 1 and 0
map_enabled_disabled() {
  local value="$1"
  if [ "$value" == "true" ]; then
    echo "1"
  else
    echo "0"
  fi
}

# Function to map 1 and 0 to "enabled" and "disabled"
map_1_0_to_enabled_disabled() {
  local value="$1"
  if [ "$value" == "1" ]; then
    echo "true"
  else
    echo "false"
  fi
}

# Function to get the value of a key from a file
get_config_value() {
  local file="$1"
  local key="$2"
  awk -F '=' '$1 == "'"$key"'" {print $2}' "$file" | head -n 1
}

set_config_value() {
  local file="$1"
  local key="$2"
  local value="$3"

  # Use sed to replace the line with the new value, or add it if it doesn't exist
  sed -i "/^${key}=/s/.*/${key}=${value}/" "$file" || echo "${key}=${value}" >> "$file"
}


# Function to generate a combobox (select element) with number values
field_number_select() {
  local name="$1"        # Name of the select element
  local label="$2"       # Label for the select element
  local selected_value="$3" # Currently selected value
  local start="$4"       # Starting number
  local end="$5"         # Ending number
  local increment="$6"   # Increment value

  echo "<div class=\"mb-3\">"
  echo "  <label for=\"$name\" class=\"form-label\">$label</label>"
  echo "  <select class=\"form-select\" id=\"$name\" name=\"$name\">"

  local current=$start
  while [ "$current" -le "$end" ]; do
    local selected=""
    if [ "$current" = "$selected_value" ]; then
      selected=" selected"
    fi
    echo "    <option value=\"$current\"$selected>$current</option>"
    current=$((current + increment))
  done

  echo "  </select>"
  echo "</div>"
}


# Define available wireless channels
channels="1 2 3 4 5 6 7 8 9 10 11 12 13 14 36 40 44 48 52 56 60 64 100 104 108 112 116 120 124 128 132 136 140 149 153 157 161 165"

# Define corresponding frequencies
frequencies="2412 2417 2422 2427 2432 2437 2442 2447 2452 2457 2462 2467 2472 2484 5180 5200 5220 5240 5260 5280 5300 5320 5500 5520 5540 5560 5580 5600 5620 5640 5660 5680 5700 5745 5765 5785 5805 5825"

# Function to get the frequency for a given channel
get_frequency() {
  local channel="$1"
  local index=0
  for c in $channels; do
    if [ "$c" = "$channel" ]; then
      # Get the corresponding frequency
      frequency=$(echo "$frequencies" | awk "{print \$$((index+1))}")
      echo "$frequency"
      return
    fi
    index=$((index+1))
  done
  echo "Unknown" # Return "Unknown" if channel not found
}

# Function to generate a dropdown select element
field_select() {
  local name="$1"
  local label="$2"
  local selected_value="$3"
  echo "<div class=\"mb-3\">"
  echo "  <label for=\"$name\" class=\"form-label\">$label</label>"
  echo "  <select class=\"form-select\" id=\"$name\" name=\"$name\">"
  # Iterate through the channels array
  for channel in $channels; do
    local frequency=$(get_frequency "$channel")
    local selected=""
    if [ "$channel" = "$selected_value" ]; then
      selected="selected"
    fi
    echo "    <option value=\"$channel\" $selected>Channel $channel - $frequency</option>"
  done
  echo "  </select>"
  echo "</div>"
}



# Define the default values or retrieve them from a config file
config_file="/tmp/config.cfg"
target_key="channel"


# Get the channel value
channel=$(get_config_value "$wfb_file" "channel" )
power=$(get_config_value "$wfb_file" "txpower")
driver_txpower_override=$(get_config_value "$wfb_file" "driver_txpower_override")

# Get config values
stbc=$(get_config_value "$wfb_file" "stbc" )
ldpc=$(get_config_value "$wfb_file" "ldpc" )

# Convert enable/disable to 1 and 0.
# Assign 1 to the variable if 0 set it to disabled
stbc=$(map_1_0_to_enabled_disabled "$stbc")
ldpc=$(map_1_0_to_enabled_disabled "$ldpc")

mcs_index=$(get_config_value "$wfb_file" "mcs_index" )

bandwidth=$(get_config_value "$wfb_file" "bandwidth" )

fec_k=$(get_config_value "$wfb_file" "fec_k" )
fec_n=$(get_config_value "$wfb_file" "fec_n" )

# Perform the conditional assignment
if [ "$channel" -lt 30 ]; then
  power="$power"
else
  power="$driver_txpower_override"
fi
  


if [ "$REQUEST_METHOD" = "POST" ]; then
        case "$POST_action" in

                update)
                        eval set > /tmp/mike

                        for p in $params; do
                                eval wfb_${p}=\$POST_wfb_${p}
                        done

                        set_config_value "$wfb_file" "channel" "$POST_channel"

                        if [ "$POST_channel" -lt 30 ]; then
                                set_config_value "$wfb_file" "txpower" "$POST_power" 
                                set_config_value "$wfb_file" "driver_txpower_override" "0" 
                        else
                                set_config_value "$wfb_file" "txpower" "0" 
                                set_config_value "$wfb_file" "driver_txpower_override" "$POST_power" 
                        fi

                        echo "POST_ldpc=$POST_ldpc" >> /tmp/mike
                        echo "POST_stbc=$POST_stbc" >> /tmp/mike

                        if [ "$POST_ldpc" = "false" ]; then
                                set_config_value "$wfb_file" "ldpc" "0"
                        else
                                set_config_value "$wfb_file" "ldpc" "1"
                        fi

                        if [ "$POST_stbc" = "false" ]; then
                                set_config_value "$wfb_file" "stbc" "0"
                        else
                                set_config_value "$wfb_file" "stbc" "1"
                        fi


                        set_config_value "$wfb_file" "mcs_index" "$POST_mcs_index"
                        set_config_value "$wfb_file" "fec_k" "$POST_fec_k"
                        set_config_value "$wfb_file" "fec_n" "$POST_fec_n"
                        set_config_value "$wfb_file" "bandwidth" "$POST_bandwidth"

                        echo "$command" >> /tmp/webui.log
                        eval "$command" > /dev/null 2>&1

                        wifibroadcast stop; sleep 2; wifibroadcast start

                        #update_caminfo
                        redirect_back "success" "Wireless settings updated."
                        ;;
        esac
fi
%>
<%in p/header.cgi %>

<div class="row g-4">
        <div class="col col-md-6 col-lg-4 mb-4">
                <form action="<%= $SCRIPT_NAME %>" method="post">
                        <% field_hidden "action" "update" %>

                        <% field_select "channel" "Wireless Channel" "$channel" %>

                        <% field_range "power" "Power" "$power" "0" "55"  %>


                        <% field_switch "stbc" "STBC Enabled" "$stbc" "" %>
                        <% field_switch "ldpc" "LDPC Enabled" "$ldpc" "" %>

                        <% field_number_select "mcs_index" "MCS Index" "$mcs_index" 1 10 1%>

                        <% field_number_select "bandwidth" "Bandwidth" "$bandwidth" 10 60 10%>
                        <% field_number_select "fec_k" "FecK" "$fec_k" 1 15 1%>
                        <% field_number_select "fec_n" "FecN" "$fec_n" 1 15 1%>

                        <% button_submit %>
                </form>

        </div>

        <div class="col col-md-6 col-lg-8">
                Related Settings
                <% ex "cat /etc/wfb.conf" %>

        </div>
</div>


<%in p/footer.cgi %>