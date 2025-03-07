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

# Function to get the value of a key from a file
get_config_value() {
  local file="$1"
  local key="$2"
  awk -F '=' '$1 == "'"$key"'" {print $2}' "$file" | head -n 1
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



# Define the default values or retrieve them from a config file
config_file="/tmp/config.cfg"
target_key="channel"


# Get the channel value
channel=$(get_config_value "$wfb_file" "channel" )
power=$(get_config_value "$wfb_file" "txpower")
driver_txpower_override=$(get_config_value "$wfb_file" "driver_txpower_override")
stbc=$(get_config_value "$wfb_file" "stbc" )
ldpc=$(get_config_value "$wfb_file" "ldpc" )
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
  echo "<h1>Here</H1>"



if [ "$REQUEST_METHOD" = "POST" ]; then
	case "$POST_action" in
		changemac)
			if echo "$POST_mac_address" | grep -Eiq '^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$'; then
				fw_setenv ethaddr "$POST_mac_address"
				update_caminfo
				touch /tmp/system-reboot
				redirect_back "success" "MACaddress updated."
			else
				if [ -z "$POST_mac_address" ]; then
					redirect_back "warning" "Empty MAC address."
				else
					redirect_back "warning" "Invalid MAC address: ${POST_mac_address}"
				fi
			fi
			;;

		reset)
			rm -f /etc/network/interfaces.d/*
			cp -f /rom/etc/network/interfaces.d/* /etc/network/interfaces.d
			redirect_back
			;;

		update)
			for p in $params; do
				eval network_${p}=\$POST_network_${p}
			done

			[ -z "$network_interface" ] && set_error_flag "Default network interface cannot be empty."
			if [ "$network_interface" = "wlan0" ]; then
				[ -z "$network_wlan_ssid" ] && set_error_flag"WLAN SSID cannot be empty."
				[ -z "$network_wlan_password" ] && set_error_flag "WLAN Password cannot be empty."
			fi

			if [ "$network_dhcp" = "false" ]; then
				network_mode="static"
				[ -z "$network_address" ] && set_error_flag "IP address cannot be empty."
				[ -z "$network_netmask" ] && set_error_flag "Networking mask cannot be empty."
			else
				network_mode="dhcp"
			fi

			if [ -z "$error" ]; then
				command="setnetwork"
				command="${command} -i $network_interface"
				command="${command} -m $network_mode"
				command="${command} -h $network_hostname"

				if [ "$network_interface" = "wlan0" ]; then
					command="${command} -s $network_wlan_ssid"
					command="${command} -p $network_wlan_password"
				fi

				if [ "$network_mode" != "dhcp" ]; then
					command="${command} -a $network_address"
					command="${command} -n $network_netmask"
					[ -n "$network_gateway" ] && command="${command} -g $network_gateway"
					[ -n "$network_nameserver" ] && command="${command} -d $network_nameserver"
				fi

				echo "$command" >> /tmp/webui.log
				eval "$command" > /dev/null 2>&1

				update_caminfo
				redirect_back "success" "Network settings updated."
			fi
			;;
	esac
fi
%>
<%in p/header.cgi %>

<div class="row g-4">
	<div class="col col-md-6 col-lg-4 mb-4">
		<form action="<%= $SCRIPT_NAME %>" method="post">
			<% field_hidden "action" "update" %>

			<% field_select "channel" "Wireless Channel" "$channel" %xxdd>

			<% field_range "power" "Power" "$power" "0" "55"  %>

			<% field_switch "stbc" "STBC Enabled" "$stbc" "" %>
			<% field_switch "ldpc" "LDPC Enabled" "$ldpc" "" %>

			<% field_number_select "mcs_index" "MCS Index" "$mcs_index" 1 10 1%>

		        <% field_number_select "bandwith" "Bandwidth" "$bandwith" 10 60 10%>
			<% field_number_select "fec_k" "FecK" "$fec_k" 1 10 1%>
			<% field_number_select "fec_k" "FecN" "$fec_n" 1 10 1%>

			<% button_submit %>
		</form>

	</div>

	<div class="col col-md-6 col-lg-8">
		Related Settings
		<% ex "cat /etc/wfb.conf" %>

		<% ex "ifconfig" %>
	</div>
</div>


<%in p/footer.cgi %>v