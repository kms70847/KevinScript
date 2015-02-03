function range(end){
    ret = [];
    if(end > 0){
        count = 0;
        while(count < end){
            ret.append(count);
            count = count + 1;
        };
    };
    return ret;
};

function Dict(){
    self = object();
    self.num_buckets = 10;
    self.buckets = [];
    for(i in range(self.num_buckets)){
        self.buckets.append([]);
    };

    self.set = function(key, value){
        bucket_idx = hash(key) % self.num_buckets;
        bucket = self.buckets.at(bucket_idx);

        for(item in bucket){
            if (key == item.at(0)){
                item.set(1, value);
                return 0;
            };
        };
        bucket.append([key, value]);
    };

    self.get = function(key){
        bucket_idx = hash(key) % self.num_buckets;
        bucket = self.buckets.at(bucket_idx);
        for (item in bucket){
            if (key == item.at(0)){
                return item.at(1);
            };
        };
    };

    self.frob = function(){return 23;};
    return self;
};

d = Dict();
d.set(23, 42);
print d.get(23);

print "ready";