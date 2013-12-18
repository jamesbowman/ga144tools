# Legal instructions for slot3:
#     over a dup pop b! a! . push

  . @p b!
    EAST
  . -
: loop
  . @p
    0x1111
  . call emit

  . call imm
  100
  2

: inner0

  . call imm
  50000
  1
: inner1
  # . call reg
  # 1
  # . call emit

  . call dec
  1
  . call jnz
    inner1
    1
  .

  . call dec
  2
  . call jnz
    inner1
    2
  .

  . @p
    0x2222
  . call emit
  . call goto
  loop
  .
  .
