function is_prime(x){
    if (x < 2){return True;}
    i = 2;
    while (i < x){
        if (x % i == 0){return False;}
        i = i + 1;
    }
    return True;
}

print "Prime numbers below 100:";
i = 2;
while(i<100){
    if (is_prime(i)){
        print i;
    }
    i = i + 1;
}