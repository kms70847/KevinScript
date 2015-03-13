override_method(List, "__repr__", function(self){
    ret = "[";
    needs_comma = False;
    for(item in self){
        if(needs_comma){
            ret = ret + ", ";
        }
        else{
            needs_comma = True;
        }
        ret = ret + item.__repr__();
    }
    ret = ret + "]";
    return ret;
});