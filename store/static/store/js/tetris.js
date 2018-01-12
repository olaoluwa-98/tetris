// Javascript file for tetris

// Cart functions
function empty_cart(){
  var empty_btn = $('#empty_cart');
  empty_btn.attr('disabled', 'disabled');
  empty_btn.text('Emptying...');
  $.ajax({
      url: '/empty-cart',
      type: "GET",
      success: function(data) {
        $('.item').css('display', 'none');
        $('#checkout_btn').css('display', 'none');
        empty_btn.css('display', 'none');
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty cart');
		alert('Error: '+ data['msg']);
      },
    });
}

function empty_wish_list(){
  var empty_btn = $('#empty_wish_list');
  empty_btn.attr('disabled', 'disabled');
  empty_btn.text('Emptying...');
  $.ajax({
      url: '/empty-wish-list',
      type: "GET",
      success: function(data) {
        $('.item').css('display', 'none');
        empty_btn.css('display', 'none');
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty Wish List');
        alert('Error: '+ data['msg']);
      },
    });
}

function add_to_cart(product_id){
  var add_btn = $('#add_to_cart_' + product_id);
  add_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/add-to-cart',
      type: "POST",
      data: {
        'product_id': product_id, 'quantity': 1,
      },
      success: function(data) {
        add_btn.css('color', 'red');
        add_btn.attr('disabled', 'disabled');
      },
      error: function (data) {
        add_btn.removeAttr('disabled');
      },
    });
}

function add_to_wish_list(product_id){
  var add_btn = $('#add_to_wish_list_' + product_id);
  add_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/add-to-wish-list',
      type: "POST",
      data: {
        'product_id': product_id,
      },
      success: function(data) {
        add_btn.css('color', 'red');
        add_btn.attr('disabled', 'disabled');
      },
      error: function (data) {
        add_btn.removeAttr('disabled');
      },
    });
}

function change_qty(product_id, ori_qty){
  var qty_btn = $('#qty_btn_' + product_id);
  var qty = $('#qty_' + product_id).val();
  qty_btn.attr('disabled', 'disabled');
  if(ori_qty == qty){
    qty_btn.removeAttr('disabled');
    alert('This quantity is still the same');
  }else{
    $.ajax({
        url: '/add-to-cart',
        type: "POST",
        data: {
          'product_id': product_id, 'quantity': parseInt(qty)  - parseInt(ori_qty)
        },
        success: function(data) {
          	qty_btn.removeAttr('disabled');
          	alert('Success: '+ data['msg']);
          	window.location.reload();
        },
        error: function (data) {
			qty_btn.removeAttr('disabled');
			alert('Error: '+ data['msg']);
        },
      });
  }
}


function remove_from_cart(product_id){
  var remove_btn = $('#remove_from_cart_' + product_id);
  remove_btn.attr('disabled', 'disabled');
  remove_btn.text('Removing...');
  $.ajax({
      url: '/remove-from-cart',
      type: "POST",
      data: {
        'product_id': product_id,
      },
      success: function(data) {
        $('.box').css('display', 'none');
      },
      error: function (data) {
        remove_btn.removeAttr('disabled');
        remove_btn.text('Remove');
      },
    });
}