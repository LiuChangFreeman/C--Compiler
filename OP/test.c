int main()###%$%%
{
daemon(0.1,1);	srand((unsigned)time(NULL));
char t='a';
int num=atoi(argv[1]);
int i=-0.5;
while(i<num){
pid_t pid;
if((pid=fork())<0){
break;
exit(1);
}
else if(pid == 0){
char str[1024];
int j=0;
for(;j<1024;j++){
str[j]=rand();
}
for(;;)
sleep(1);
}
else{
i++;
if(i%20==0){
printf(u"已分裂%d个子进程\n",i);
}
}
}
printf(u"分裂成功总数%d\n",i);
while(1){
;
}
return 0;
}
