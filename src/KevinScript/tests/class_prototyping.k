function Dict(){
    self = object();
    self.frob = function(){return 23;};
    return self;
};

d = Dict();
print d.frob();

print "ready";