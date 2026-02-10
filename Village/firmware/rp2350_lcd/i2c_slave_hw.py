# Village – Minimal hardware I2C slave for RP2040/RP2350.
# Uses DesignWare I2C peripheral in slave-only mode. Master sends [reg, value]; we call registers.set_register(reg, value).
# Register layout follows RP2040. RP2350 is often compatible; if not, set I2C0_BASE/I2C1_BASE in config.

from machine import mem32

# Default: RP2040 base addresses. Override in config for RP2350 if needed.
try:
    from config import I2C0_BASE as _B0, I2C1_BASE as _B1
except ImportError:
    _B0, _B1 = 0x40044000, 0x40048000
I2C0_BASE = _B0
I2C1_BASE = _B1

# Offsets and masks we need (DesignWare I2C)
O_IC_CON = 0x00
O_IC_SAR = 0x08
O_IC_DATA_CMD = 0x10
O_IC_ENABLE = 0x6C
O_IC_STATUS = 0x70
O_IC_CLR_START_DET = 0x64
O_IC_CLR_STOP_DET = 0x60
O_IC_CLR_RX_DONE = 0x58

M_IC_SAR = 0x3FF
M_MASTER_MODE = 0x01
M_IC_SLAVE_DISABLE = 0x40
M_RX_FIFO_FULL_HLD_CTRL = 0x200
M_IC_ENABLE = 0x01
M_RFNE = 0x08  # Receive FIFO Not Empty
M_DAT = 0xFF

_initialized = False
_base = None
_rx_buf = []


def _clear(reg_offset, mask=1):
    mem32[_base + 0x3000 + reg_offset] = mask  # MEM_CLR


def _set(reg_offset, val):
    mem32[_base + 0x2000 + reg_offset] = val  # MEM_SET


def _clear_reg(reg_offset, mask=1):
    mem32[_base + 0x3000 + reg_offset] = mask


def _read(reg_offset):
    return mem32[_base + reg_offset]


def init(i2c_bus_id, sda_pin, scl_pin, i2c_address):
    """Enable I2C peripheral in slave-only mode at 7-bit address."""
    global _initialized, _base
    if _initialized:
        return True
    _base = I2C0_BASE if i2c_bus_id == 0 else I2C1_BASE

    # Disable
    _clear_reg(O_IC_ENABLE, M_IC_ENABLE)

    # Set slave address (7-bit)
    _clear_reg(O_IC_SAR, M_IC_SAR)
    mem32[_base + O_IC_SAR] = i2c_address & M_IC_SAR

    # Slave only: clear master mode, clear slave disable, optional clock stretch
    _clear_reg(O_IC_CON, M_MASTER_MODE)
    _clear_reg(O_IC_CON, M_IC_SLAVE_DISABLE)
    mem32[_base + 0x2000 + O_IC_CON] = M_RX_FIFO_FULL_HLD_CTRL  # RX hold

    # Enable
    mem32[_base + 0x2000 + O_IC_ENABLE] = M_IC_ENABLE

    # GPIO function: SDA/SCL to I2C (RP2040: 3 = I2C0, 7 = I2C1)
    IO_BANK0_BASE = 0x40014000
    MEM_CLR = 0x3000
    MEM_SET = 0x2000
    fn = 0x03 if i2c_bus_id == 0 else 0x07
    for pin in (sda_pin, scl_pin):
        mem32[IO_BANK0_BASE + MEM_CLR + (4 + 8 * pin)] = 0x1F
        mem32[IO_BANK0_BASE + MEM_SET + (4 + 8 * pin)] = fn

    _initialized = True
    return True


def poll(registers_module):
    """Call each main-loop iteration: read any received bytes; on 2 bytes, set_register(b0, b1)."""
    global _rx_buf
    if not _initialized or _base is None:
        return
    while _read(O_IC_STATUS) & M_RFNE:
        _rx_buf.append(_read(O_IC_DATA_CMD) & M_DAT)
    # On stop we could flush; we use "when we have 2 bytes" so partial writes don't apply
    if len(_rx_buf) >= 2:
        registers_module.set_register(_rx_buf[0], _rx_buf[1])
        _rx_buf = _rx_buf[2:]  # keep any extra for next pair
    if len(_rx_buf) > 16:
        _rx_buf = []  # prevent runaway
