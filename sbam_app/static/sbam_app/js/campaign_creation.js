$(document).ready(function(){
    console.log(domainstreeData);
    console.log(usertreeData);
    const myTree = new Tree('#dim_tree_container', {
        data: domainstreeData,

        onChange: function() {
            $("#selected_domains tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            for(var i=0; i < len; i++){
                if (this.selectedNodes[i].id.includes('domain'))
                    $("#selected_domains tbody").append("<tr class=\"table-info\"><th scope=\"row\">"+i+"</th><td>"+this.selectedNodes[i].text+"</td></tr>");
            }
        },
    });

    const userTree = new Tree('#user_tree_container', {
        data: usertreeData,

        // onChange: function() {
        //     $("#selected_domains tr").remove();
        //     console.log(this.selectedNodes);
        //     var len = this.selectedNodes.length;
        //     for(var i=0; i < len; i++){
        //         if (this.selectedNodes[i].id.includes('domain'))
        //             $("#selected_domains tbody").append("<tr><th scope=\"row\">"+i+"</th><td>"+this.selectedNodes[i].text+"</td></tr>");
        //     }
        // },
    });

});