addiu $sp,$zero,0x10018000
or $fp,$sp,$zero
jal  main
jal  end

f1:
lw $14,0($fp)
lw $15,4($fp)
sub $fp,$fp,8
sgt $16,$14,$15
bgt $16,$zero,l1
j l2
l1:
add $v0,$zero,$14
jr $ra
l2:
add $v0,$zero,$15
jr $ra

f2:
lw $17,0($fp)
lw $10,4($fp)
sub $fp,$fp,8
slt $11,$17,$10
bgt $11,$zero,l4
j l5
l4:
add $v0,$zero,$17
jr $ra
l5:
add $v0,$zero,$10
jr $ra

f3:
lw $12,0($fp)
sub $fp,$fp,4
add $a2,$zero,1
slt $13,$12,$a2
bgt $13,$zero,l7
j l8
l7:
add $v0,$zero,1
jr $ra
l8:
sub $sp,$sp,8
sw $ra,4($sp)
sw $12,0($sp)
add $a2,$zero,1
sub $21,$12,$a2
add $fp,$fp,4
sw $21,0($fp)
jal  f3
lw $12,0($sp)
lw $ra,4($sp)
add $sp,$sp,8
add $20,$zero,$v0
mul $23,$12,$20
add $v0,$zero,$23
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
add $22,$zero,$v0
add $18,$zero,$22
add $19,$zero,1
add $24,$zero,234
add $8,$zero,2
add $a1,$zero,3
add $a2,$zero,4
mul $9,$a1,$a2
add $7,$9,5
add $a2,$zero,6
sub $25,$7,$a2
add $14,$zero,1
add $15,$zero,1
l18:
add $a2,$zero,100
slt $16,$15,$a2
bgt $16,$zero,l16
j l17
l16:
add $a2,$zero,50
slt $17,$15,$a2
bgt $17,$zero,l10
j l11
l10:
j l19
j l12
l11:
add $14,$14,$15
l12:
add $a2,$zero,98
sgt $10,$15,$a2
bgt $10,$zero,l13
j l14
l13:
j l17
j l15
l14:
add $8,$8,$25
add $a1,$zero,5
add $a2,$zero,4
mul $11,$a1,$a2
add $24,$zero,$11
add $a1,$zero,1
add $12,$a1,1
add $18,$zero,$12
l15:
l19:
add $15,$15,1
j l18
l17:
sub $sp,$sp,4
sw $ra,0($sp)
add $fp,$fp,8
sw $8,0($fp)
sw $25,4($fp)
jal  f2
lw $ra,0($sp)
add $sp,$sp,4
add $13,$zero,$v0
add $a1,$zero,1
add $a2,$zero,2
mul $21,$a1,$a2
add $20,$21,3
add $a1,$zero,4
add $a2,$zero,8
mul $23,$a1,$a2
div $22,$20,$23
add $a2,$zero,6
sub $9,$22,$a2
add $7,$9,$19
sub $14,$7,$24
add $15,$14,$13
l22:
add $a2,$zero,40
slt $16,$15,$a2
bgt $16,$zero,l20
j l21
l20:
add $15,$15,$19
j l22
l21:
add $a1,$zero,534
add $a2,$zero,23
sub $17,$a1,$a2
add $10,$17,423
add $a2,$zero,23
mul $11,$10,$a2
add $12,$11,$15
add $v0,$zero,$12
jr $ra
end: