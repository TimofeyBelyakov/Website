$(document).ready(function (){
    var f = document.getElementById('filter');
    f.all.onchange = function(e){
        var el = e.target || e.srcElement;

        if(el.checked){
            $("input[name=category]").prop({ checked : true });
        }
        else{
            $("input[name=category]").prop({ checked : false });
        }
    };
});