override_method(Object, "__repr__", function(self){
    return "<Object instance>";
});

override_method(Object, "__init__", function(self){;});

override_method(Boolean, "__and__", function(self, other){
    if(self){
        if(other){return True;}
        else{return False;}
    }
    else{
        return False;
    }
});

override_method(Boolean, "__or__", function(self, other){
    if(self){
        return True;
    }
    else{
        if(other){return True;}
        else{return False;}
    }
});

override_method(Boolean, "__repr__", function(self){
    if(self){return "True";}
    else{return "False";}
});

override_method(Nonetype, "__repr__", function(self){
    return "None";
});

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