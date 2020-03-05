// $(document).ready(function(){
//
//     function create_dimesnions_list() {
//         var dimensions = [];
//         $('.dimension').each(function(i, obj){
//             var my_list = [];
//             var dimension_id = $(this).data("id");
//             var dimension_title = $(this).data("title");
//             var dimension_level = $(this).data("level");
//             my_list.push(dimension_id, dimension_level, dimension_title);
//             dimensions.push(my_list);
//         });
//         return dimensions;
//     }
//
//     function create_domains_list() {
//         var domains = [];
//         $('.domain').each(function(i, obj){
//             var my_list = [];
//             var domain_id = $(this).data("id");
//             var domain_title = $(this).data("title");
//             var dimension_id = $(this).data("dimension_id");
//             my_list.push(domain_id, domain_title, dimension_id);
//             domains.push(my_list);
//         });
//         return domains;
//     }
//
//     // var dims = create_dimesnions_list();
//     // alert(dims)
//
//     // var doms = create_domains_list();
//     // alert(doms)
//
//     function create_tree_view() {
//          var dims = create_dimesnions_list();
//          var doms = create_domains_list();
//
//     }
//
//     // });
// });




$(document).ready(function(){
    console.log(treeData);

    const myTree = new Tree('#dim_tree_container', {
      data: treeData,
    });
});