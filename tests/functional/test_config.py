"""
Test R-Config and I-Config Read, Write, and Erase L3 commands.

Mirrors:
    - libtropic-upstream/tests/functional/lt_test_rev_read_r_config.c
    - libtropic-upstream/tests/functional/lt_test_rev_write_r_config.c
    - libtropic-upstream/tests/functional/lt_test_rev_read_i_config.c
    - libtropic-upstream/tests/functional/lt_test_ire_write_i_config.c

Tests device configuration operations.

WARNING: I-Config tests are IRREVERSIBLE and permanently modify the device!
"""

import pytest

from libtropic import ConfigAddress, Tropic01
from libtropic.types import DeviceConfig


@pytest.mark.hardware
@pytest.mark.destructive
class TestRConfigRead:
    """
    Tests for R_Config_Read command.

    Maps to: lt_test_rev_read_r_config()
    """

    def test_read_r_config_all_addresses(self, device_with_session: Tropic01) -> None:
        """Test reading all R-Config addresses."""
        addresses = [
            ConfigAddress.START_UP,
            ConfigAddress.SENSORS,
            ConfigAddress.DEBUG,
            ConfigAddress.GPO,
            ConfigAddress.SLEEP_MODE,
            ConfigAddress.UAP_PAIRING_KEY_WRITE,
            ConfigAddress.UAP_PAIRING_KEY_READ,
            ConfigAddress.UAP_PAIRING_KEY_INVALIDATE,
            ConfigAddress.UAP_R_CONFIG_WRITE_ERASE,
            ConfigAddress.UAP_R_CONFIG_READ,
            ConfigAddress.UAP_I_CONFIG_WRITE,
            ConfigAddress.UAP_I_CONFIG_READ,
            ConfigAddress.UAP_PING,
            ConfigAddress.UAP_R_MEM_DATA_WRITE,
            ConfigAddress.UAP_R_MEM_DATA_READ,
            ConfigAddress.UAP_R_MEM_DATA_ERASE,
            ConfigAddress.UAP_RANDOM_VALUE_GET,
            ConfigAddress.UAP_ECC_KEY_GENERATE,
            ConfigAddress.UAP_ECC_KEY_STORE,
            ConfigAddress.UAP_ECC_KEY_READ,
            ConfigAddress.UAP_ECC_KEY_ERASE,
            ConfigAddress.UAP_ECDSA_SIGN,
            ConfigAddress.UAP_EDDSA_SIGN,
            ConfigAddress.UAP_MCOUNTER_INIT,
            ConfigAddress.UAP_MCOUNTER_GET,
            ConfigAddress.UAP_MCOUNTER_UPDATE,
            ConfigAddress.UAP_MAC_AND_DESTROY,
        ]

        for address in addresses:
            value = device_with_session.config.read_r(address)
            # Value should be a 32-bit integer
            assert 0 <= value <= 0xFFFFFFFF, f"Address {address}: Invalid value {value}"

    def test_read_all_r_config(self, device_with_session: Tropic01) -> None:
        """Test reading all R-Config as DeviceConfig object."""
        config: DeviceConfig = device_with_session.config.read_all_r()

        # Verify all fields are valid 32-bit integers
        assert 0 <= config.start_up <= 0xFFFFFFFF
        assert 0 <= config.sensors <= 0xFFFFFFFF
        assert 0 <= config.debug <= 0xFFFFFFFF
        assert 0 <= config.uap_ping <= 0xFFFFFFFF

@pytest.mark.hardware
@pytest.mark.destructive
class TestRConfigReadWrite:
    """
    Tests for R_Config_Write command.

    Maps to: lt_test_rev_write_r_config()
    """

    def test_read_erase_write_r_config(self, device_with_session: Tropic01) -> None:
        """
        Test writing and reading R-Config values using a full Read-Modify-Write cycle.
        
        Sequence:
        1. Read entire R-Config state (Backup).
        2. Erase R-Config on device.
        3. Verify all R-Config words are erased (0xFFFFFFFF).
        4. Prepare modified state locally (Backup + Test Values).
        5. Write full modified state.
        6. Verify changes.
        7. Restore original state 
            7.1 - Erase
            7.2 - Verify Erase
            7.3 - Restore original values
        """
        
        # 1. Read the entire R-Config to capture full device state
        full_original_config: dict[ConfigAddress, int] = {}
        for address in ConfigAddress:
            full_original_config[address] = device_with_session.config.read_r(address)

        try:
            # 2. Erase R-Config
            device_with_session.config.erase_r()

            # 3. Verify that the Erase was successful for ALL addresses
            for address in ConfigAddress:
                val = device_with_session.config.read_r(address)
                assert val == 0xFFFFFFFF, (
                    f"Post-Erase Check Failed at {address.name} (0x{address.value:04X}): "
                    f"Expected 0xFFFFFFFF, got 0x{val:08X}"
                )

            # 4. Prepare the data structure: Original Data + Desired Changes
            config_to_write = full_original_config.copy()
            
            test_updates = {
                ConfigAddress.UAP_PING: 0xAAAAAAAA,
                ConfigAddress.UAP_RANDOM_VALUE_GET: 0x55555555,
            }
            config_to_write.update(test_updates)

            # 5. Write the full modified set
            for address, value in config_to_write.items():
                device_with_session.config.write_r(address, value)

            # 6. Verify data integrity of the changes
            for address, expected in test_updates.items():
                actual = device_with_session.config.read_r(address)
                assert actual == expected, (
                    f"Write Verify Failed at {address.name}: Expected 0x{expected:08X}, got 0x{actual:08X}"
                )

        finally:
            # 7. Restore original state 
            #    Erase, verify and write back the original configuration
            # 7.1 - Erase
            device_with_session.config.erase_r()
            # 7.2 - Verify Erase
            for address in ConfigAddress:
                val = device_with_session.config.read_r(address)
                assert val == 0xFFFFFFFF, (
                    f"Post-Erase Check Failed at {address.name} (0x{address.value:04X}): "
                    f"Expected 0xFFFFFFFF, got 0x{val:08X}"
                )
            # 7.3 - Restore original values
            for address, value in full_original_config.items():
                device_with_session.config.write_r(address, value)


@pytest.mark.hardware
@pytest.mark.destructive
class TestIConfigRead:
    """
    Tests for I_Config_Read command.

    Maps to: lt_test_rev_read_i_config()
    """

    def test_read_i_config_all_addresses(self, device_with_session: Tropic01) -> None:
        """Test reading all I-Config addresses."""
        addresses = [
            ConfigAddress.START_UP,
            ConfigAddress.SENSORS,
            ConfigAddress.DEBUG,
            ConfigAddress.GPO,
            ConfigAddress.SLEEP_MODE,
            ConfigAddress.UAP_PAIRING_KEY_WRITE,
            ConfigAddress.UAP_PAIRING_KEY_READ,
            ConfigAddress.UAP_PAIRING_KEY_INVALIDATE,
            ConfigAddress.UAP_R_CONFIG_WRITE_ERASE,
            ConfigAddress.UAP_R_CONFIG_READ,
            ConfigAddress.UAP_I_CONFIG_WRITE,
            ConfigAddress.UAP_I_CONFIG_READ,
            ConfigAddress.UAP_PING,
            ConfigAddress.UAP_R_MEM_DATA_WRITE,
            ConfigAddress.UAP_R_MEM_DATA_READ,
            ConfigAddress.UAP_R_MEM_DATA_ERASE,
            ConfigAddress.UAP_RANDOM_VALUE_GET,
            ConfigAddress.UAP_ECC_KEY_GENERATE,
            ConfigAddress.UAP_ECC_KEY_STORE,
            ConfigAddress.UAP_ECC_KEY_READ,
            ConfigAddress.UAP_ECC_KEY_ERASE,
            ConfigAddress.UAP_ECDSA_SIGN,
            ConfigAddress.UAP_EDDSA_SIGN,
            ConfigAddress.UAP_MCOUNTER_INIT,
            ConfigAddress.UAP_MCOUNTER_GET,
            ConfigAddress.UAP_MCOUNTER_UPDATE,
            ConfigAddress.UAP_MAC_AND_DESTROY,
        ]

        for address in addresses:
            value = device_with_session.config.read_i(address)
            # Value should be a 32-bit integer
            assert 0 <= value <= 0xFFFFFFFF, f"Address {address}: Invalid value {value}"

    def test_read_all_i_config(self, device_with_session: Tropic01) -> None:
        """Test reading all I-Config as DeviceConfig object."""
        config: DeviceConfig = device_with_session.config.read_all_i()

        # Verify all fields are valid 32-bit integers
        assert 0 <= config.start_up <= 0xFFFFFFFF
        assert 0 <= config.sensors <= 0xFFFFFFFF
        assert 0 <= config.debug <= 0xFFFFFFFF
        assert 0 <= config.uap_ping <= 0xFFFFFFFF


@pytest.mark.hardware
@pytest.mark.irreversible
class TestIConfigWrite:
    """
    Tests for I_Config_Write command.

    Maps to: lt_test_ire_write_i_config()

    WARNING: These tests PERMANENTLY modify the device! They can only set
    bits to 0, never back to 1. Only run on test/development devices!
    """

    def test_write_i_config_bit_warning(self, device_with_session: Tropic01) -> None:
        """
        This test demonstrates I-Config write but DOES NOT execute it
        to prevent accidental permanent modification.

        To actually test I-Config write, use a dedicated test device
        and uncomment the write operation.
        """
        # Read current value
        current = device_with_session.config.read_i(ConfigAddress.UAP_PING)

        # Find a bit that is currently 1 (can be set to 0)
        # WARNING: This is IRREVERSIBLE!

        # DO NOT UNCOMMENT unless you understand the consequences:
        # device_with_session.config.write_i_bit(ConfigAddress.UAP_PING, bit_index=0)

        # This test intentionally does nothing to prevent accidents
        assert current is not None  # Just verify we can read

    def test_write_all_i_config_warning(self, device_with_session: Tropic01) -> None:
        """
        This test demonstrates I-Config write_all but DOES NOT execute it.

        WARNING: write_all_i() permanently sets 0-bits in the config!
        """
        # Read current I-Config
        current_config: DeviceConfig = device_with_session.config.read_all_i()

        # DO NOT UNCOMMENT unless you understand the consequences:
        # The following would permanently set any 0-bits in new_config:
        # new_config = DeviceConfig(uap_ping=0xFFFFFFFE)  # Clear bit 0
        # device_with_session.config.write_all_i(new_config)

        # This test intentionally does nothing to prevent accidents
        assert current_config is not None  # Just verify we can read

