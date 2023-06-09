// Code generated by "stringer -type=HardwareType -trimprefix=HardwareType"; DO NOT EDIT.

package ethernet

import "strconv"

func _() {
	// An "invalid array index" compiler error signifies that the constant values have changed.
	// Re-run the stringer command to generate them again.
	var x [1]struct{}
	_ = x[HardwareTypeReserved-0]
	_ = x[HardwareTypeEthernet-1]
	_ = x[HardwareTypeExpEth-2]
	_ = x[HardwareTypeAX25-3]
	_ = x[HardwareTypeChaos-4]
	_ = x[HardwareTypeIEEE802-5]
	_ = x[HardwareTypeFiberChannel-18]
	_ = x[HardwareTypeSerialLine-19]
	_ = x[HardwareTypeHIPARP-28]
	_ = x[HardwareTypeIPARPISO7163-29]
	_ = x[HardwareTypeARPSec-30]
	_ = x[HardwareTypeIPSec-31]
	_ = x[HardwareTypeInfiniBand-32]
}

const (
	_HardwareType_name_0 = "ReservedEthernetExpEthAX25ChaosIEEE802"
	_HardwareType_name_1 = "FiberChannelSerialLine"
	_HardwareType_name_2 = "HIPARPIPARPISO7163ARPSecIPSecInfiniBand"
)

var (
	_HardwareType_index_0 = [...]uint8{0, 8, 16, 22, 26, 31, 38}
	_HardwareType_index_1 = [...]uint8{0, 12, 22}
	_HardwareType_index_2 = [...]uint8{0, 6, 18, 24, 29, 39}
)

func (i HardwareType) String() string {
	switch {
	case i <= 5:
		return _HardwareType_name_0[_HardwareType_index_0[i]:_HardwareType_index_0[i+1]]
	case 18 <= i && i <= 19:
		i -= 18
		return _HardwareType_name_1[_HardwareType_index_1[i]:_HardwareType_index_1[i+1]]
	case 28 <= i && i <= 32:
		i -= 28
		return _HardwareType_name_2[_HardwareType_index_2[i]:_HardwareType_index_2[i+1]]
	default:
		return "HardwareType(" + strconv.FormatInt(int64(i), 10) + ")"
	}
}
