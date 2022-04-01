addiu $sp,$zero,0x10018000
or $fp,$sp,$zero
jal  main
jal  end

f1:
lw $22,0($fp)
lw $25,4($fp)
sub $fp,$fp,8
sgt $24,$22,$25
bgt $24,$zero,l1
j l2
l1:
add $v0,$zero,$22
jr $ra
l2:
add $v0,$zero,$25
jr $ra

f2:
lw $11,0($fp)
lw $10,4($fp)
sub $fp,$fp,8
slt $13,$11,$10
bgt $13,$zero,l4
j l5
l4:
add $v0,$zero,$11
jr $ra
l5:
add $v0,$zero,$10
jr $ra

f3:
lw $12,0($fp)
sub $fp,$fp,4
add $a2,$zero,1
slt $15,$12,$a2
bgt $15,$zero,l7
j l8
l7:
add $v0,$zero,1
jr $ra
l8:
sub $sp,$sp,8
sw $ra,4($sp)
sw $12,0($sp)
add $a2,$zero,1
sub $14,$12,$a2
add $fp,$fp,4
sw $14,0($fp)
jal  f3
lw $12,0($sp)
lw $ra,4($sp)
add $sp,$sp,8
add $17,$zero,$v0
mul $7,$12,$17
add $v0,$zero,$7
jr $ra

main:
sub $sp,$sp,4
sw $ra,0($sp)
add $fp,$fp,4
add $a0,$zero,5
sw $a0,0($fp)
jal  f3
lw $ra,0($sp)
add $sp,$sp,4
add $16,$zero,$v0
add $18,$zero,$16
add $19,$zero,1
add $9,$zero,234
add $8,$zero,2
add $a1,$zero,3
add $a2,$zero,4
mul $21,$a1,$a2
add $20,$21,5
add $a2,$zero,6
sub $23,$20,$a2
add $22,$zero,1
add $25,$zero,1
l18:
add $a2,$zero,100
slt $24,$25,$a2
bgt $24,$zero,l16
j l17
l16:
add $a2,$zero,50
slt $11,$25,$a2
bgt $11,$zero,l10
j l11
l10:
j l19
j l12
l11:
add $22,$22,$25
l12:
add $a2,$zero,98
sgt $10,$25,$a2
bgt $10,$zero,l13
j l14
l13:
j l17
j l15
l14:
add $8,$8,$23
add $a1,$zero,5
add $a2,$zero,4
mul $13,$a1,$a2
add $9,$zero,$13
add $a1,$zero,1
add $12,$a1,1
add $18,$zero,$12
l15:
l19:
add $25,$25,1
j l18
l17:
sub $sp,$sp,4
sw $ra,0($sp)
add $fp,$fp,8
sw $8,0($fp)
sw $23,4($fp)
jal  f2
lw $ra,0($sp)
add $sp,$sp,4
add $15,$zero,$v0
add $a1,$zero,1
add $a2,$zero,2
mul $14,$a1,$a2
add $17,$14,3
add $a1,$zero,4
add $a2,$zero,8
mul $7,$a1,$a2
div $16,$17,$7
add $a2,$zero,6
sub $21,$16,$a2
add $20,$21,$19
sub $22,$20,$9
add $25,$22,$15
l22:
add $a2,$zero,40
slt $24,$25,$a2
bgt $24,$zero,l20
j l21
l20:
add $25,$25,$19
j l22
l21:
add $a1,$zero,534
add $a2,$zero,23
sub $11,$a1,$a2
add $10,$11,423
add $a2,$zero,23
mul $13,$10,$a2
add $12,$13,$25
add $v0,$zero,$12
jr $ra
end:
