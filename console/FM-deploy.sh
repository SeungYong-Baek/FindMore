ssh findmore rm -rf /home/seungyong/FindMore
ssh findmore mkdir /home/seungyong/FindMore
scp -r /home/seungyong/FindMore/* findmore:/home/seungyong/FindMore/
ssh findmore ls -al /home/seungyong/FindMore
ls -al /home/seungyong/FindMore
