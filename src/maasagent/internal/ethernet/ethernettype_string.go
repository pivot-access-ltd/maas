// Code generated by "stringer -type=EthernetType -trimprefix=EthernetType"; DO NOT EDIT.

package ethernet

import "strconv"

func _() {
	// An "invalid array index" compiler error signifies that the constant values have changed.
	// Re-run the stringer command to generate them again.
	var x [1]struct{}
	_ = x[EthernetTypeLLC-0]
	_ = x[EthernetTypeIPv4-2048]
	_ = x[EthernetTypeARP-2054]
	_ = x[EthernetTypeIPv6-34525]
	_ = x[EthernetTypeVLAN-33024]
	_ = x[NonStdLenEthernetTypes-1536]
}

const (
	_EthernetType_name_0 = "LLC"
	_EthernetType_name_1 = "NonStdLenEthernetTypes"
	_EthernetType_name_2 = "IPv4"
	_EthernetType_name_3 = "ARP"
	_EthernetType_name_4 = "VLAN"
	_EthernetType_name_5 = "IPv6"
)

func (i EthernetType) String() string {
	switch {
	case i == 0:
		return _EthernetType_name_0
	case i == 1536:
		return _EthernetType_name_1
	case i == 2048:
		return _EthernetType_name_2
	case i == 2054:
		return _EthernetType_name_3
	case i == 33024:
		return _EthernetType_name_4
	case i == 34525:
		return _EthernetType_name_5
	default:
		return "EthernetType(" + strconv.FormatInt(int64(i), 10) + ")"
	}
}
