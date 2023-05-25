#!/usr/bin/env bash
#  SPDX-License-Identifier: BSD-3-Clause
#  Copyright (C) 2023 Intel Corporation
#  All rights reserved.
#
set +e

yn() {
	local -A yn=()
	local _yn

	yn["y"]=0 yn["n"]=1

	while read -rp "$* (y|N)> " _yn || true; do
		_yn=${_yn::1} _yn=${_yn,,} _yn=${_yn:-n}
		[[ -n ${yn["$_yn"]} ]] && return "${yn["$_yn"]}"
	done
}

elevate() {
	((UID != 0)) || return 0

	if yn "You ($UID) need to be root to commit any changes. Elevate privileges?"; then
		exec sudo -E "$rootdir/scripts/setup.sh" interactive
	fi
}

stdin() {
	[[ ! -t 0 ]] || return 0

	echo "Requested interactive mode but stdin is not attached to a terminal, bailing" >&2
	return 1
}

main_menu() {
	local type=all answer

	stdin || return 1
	elevate

	while ((1)); do
		cat <<- MENU

			1) List PCI Devices [Currently Listing: "$type"]
			2) Change Devices To List
			3) Mark Device As Blocked (${PCI_BLOCKED:-none})
			4) Mark Device As Allowed (${PCI_ALLOWED:-none})
			5) Override Device In-Use Status
			$([[ $os == Linux ]] && echo "6) Bind Device")

			c) configure
			s) status
			r) reset
			$([[ $os == Linux ]] && echo "hp) hugepages")

			Q) Quit
			U) Update Devices View

		MENU

		read -rp "> " answer || answer=q

		case "${answer,,}" in
			1) pdevices ;;
			2) ctype && pdevices ;;
			3) fdevices 0 ;;
			4) fdevices 1 ;;
			5) odevices ;;
			6) bdevices ;;
			q) yn "Are you sure you want to quit?" && return 1 ;;
			c | commit | config)
				yn "Are you sure you want jump to config mode?" || continue
				mode=config
				return
				;;
			s | status) status ;;
			r | reset)
				yn "Are you sure you want jump to reset mode?" || continue
				mode=reset
				return
				;;
			u | update)
				CMD=reset cache_pci_bus
				collect_devices
				;;
			hp) hugepages ;;
		esac
	done
}

gdevices() {
	if [[ $type == all ]]; then
		local -gn dev_ref=all_devices_d
	else
		local -gn dev_ref=${type}_d
	fi
}

pdevices() {
	gdevices

	local use_map=()
	use_map[0]="not used" use_map[1]="used"

	if ((${#dev_ref[@]} == 0)); then
		echo "No devices found"
	else
		for dev in "${!dev_ref[@]}"; do
			echo "- $dev [${use_map[all_devices_d["$dev"]]}, ${drivers_d["$dev"]:-none}]"
		done
	fi
}

ctype() {
	local type_to_set
	local -n types_ref=types_d

	while read -rp "(${!types_ref[*]} all)> " type_to_set; do
		type_to_set=${type_to_set,,}
		if [[ -z $type_to_set ]]; then
			return
		elif [[ -n ${types_ref["$type_to_set"]} || $type_to_set == all ]]; then
			type=$type_to_set
			return
		fi
	done
}

fdevices() {
	local action=${1:-0} bdf
	local am=()
	local -gA action_0 action_1

	am[0]=PCI_BLOCKED am[1]=PCI_ALLOWED

	gdevices
	local -n action_ref=action_${action}
	local -n action_ref_rev=action_$((!action))

	while read -rp "(${!am[action]:-BDF})> " bdf; do
		bdf=${bdf,,}
		if [[ -z $bdf ]]; then
			return
		elif [[ -n ${dev_ref["$bdf"]} ]]; then
			if [[ -n ${action_ref["$bdf"]} ]]; then
				unset -v "action_ref[$bdf]"
			else
				action_ref["$bdf"]=1
				unset -v "action_ref_rev[$bdf]"
			fi
			eval "${am[action]}='${!action_ref[*]}'"
			eval "${am[!action]}='${!action_ref_rev[*]}'"
		elif [[ -z ${dev_ref["$bdf"]} ]]; then
			unset -v "action_ref[$bdf]"
			eval "${am[action]}='${!action_ref[*]}'"
		fi
	done
}

odevices() {
	local bdf

	type=all gdevices

	while read -rp "(BDF)> " bdf; do
		bdf=${bdf,,}
		if [[ -z $bdf ]]; then
			return
		elif [[ -n ${dev_ref["$bdf"]} ]]; then
			dev_ref["$bdf"]=$((!dev_ref["$bdf"]))
		fi
	done
}

bdevices() {
	[[ $os == Linux ]] || return 0

	local bdfd bdf driver

	gdevices

	while read -rp "(BDF->driver)> " bdfd; do
		bdfd=${bdfd,,}
		if [[ -z $bdfd ]]; then
			return
		fi

		bdf=${bdfd/->*/} driver=${bdfd/*->/}

		if [[ $driver == "${drivers_d["$bdf"]}" ]]; then
			echo "$bdf already bound to $driver"
			continue
		fi

		if [[ -n ${dev_ref["$bdf"]} && -n $driver ]]; then
			if yn "$bdf currently bound to ${drivers_d["$bdf"]:-none}. Bind to $driver?"; then
				linux_bind_driver "$bdf" "$driver"
			fi
		fi
	done
}

status() {
	local _os=${os,,}

	if [[ $(type -t "status_${_os}") == function ]]; then
		"status_${_os}"
	fi
}

hugepages() {
	[[ $os == Linux ]] || return 0
	local hp

	HUGE_EVEN_ALLOC=no
	while read -rp "('clear' 'even' 'commit' HUGEMEM[=$HUGEMEM MB])> " hp; do
		hp=${hp,,}
		if [[ -z $hp ]]; then
			return
		elif [[ $hp == clear ]]; then
			clear_hugepages
			return
		elif [[ $hp == even ]]; then
			HUGE_EVEN_ALLOC=yes
		elif [[ $hp =~ ^[1-9][0-9]*$ ]]; then
			NRHUGE=""
			HUGEMEM=$hp
		elif [[ $hp == commit ]]; then
			set_hp
			configure_linux_hugepages
			return
		fi
	done
}