$.fn.toggle2classes = function(class1, class2){
    if( !class1 || !class2 )
        return this;

    return this.each(function(){
        var $elm = $(this);

        if( $elm.hasClass(class1) || $elm.hasClass(class2) )
            $elm.toggleClass(class1 +' '+ class2);

        else
            $elm.addClass(class1);
    });
};