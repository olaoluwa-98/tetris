// Javascript file for tetris

function purchase(){
  var purchase_btn = $('#purchase_btn');
  if (confirm("Are you sure you want to purchase these?") == true) {
    purchase_btn.attr('disabled', 'disabled');
    purchase_btn.text('Purchasing...');
    $.ajax({
      url: '/make-purchase',
      type: "GET",
      success: function(data) {
        $('#checkout_btn').css('display', 'none');
        purchase_btn.css('display', 'none');
        window.location.replace("/orders");
      },
      error: function (data) {
        purchase_btn.removeAttr('disabled');
        purchase_btn.text('Purchase All');
        alert('Error: '+ data['responseJSON']['msg']);
        if (data['responseJSON']['shipping'])
        {
          window.location.replace("/shipping-addresses");
        }
        else if (data['responseJSON']['profile'])
        {
          window.location.replace("/profile");
        }
        else if (data['responseJSON']['quantity'])
        {
          document.getElementById(data['responseJSON']['qty']).focus();
        }
        else if (data['responseJSON']['out_of_stock'])
        {
          document.getElementById(data['responseJSON']['qty']).focus();
        }
      },
    });

  } else {
  }
}


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
        $('#cart_count').text(0);
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty cart');
		    alert('Error: '+ data['responseJSON']['msg']);
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
        wish_list_count = $('#wish_list_count').text();
        $('#wish_list_count').text(0);
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty Wish List');
        alert('Error: '+ data['responseJSON']['msg']);
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
        add_btn.attr('onclick', 'remove_from_cart(' + product_id +')');
        add_btn.attr('id', 'remove_from_cart_' + product_id);
        if ( add_btn.text().search('Add to Cart') != -1 ) {
          add_btn.text('Remove from Cart');
          add_btn.css('color', '');
          add_btn.removeClass('is-dark');
          add_btn.addClass('is-light');
        }
        cart_count = $('#cart_count').text();
        $('#cart_count').text(parseInt(cart_count) + 1);
        add_btn.removeAttr('disabled');
      },
      error: function (data) {
        add_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
      },
    });
}

function remove_from_cart(product_id){
  var remove_btn = $('#remove_from_cart_' + product_id);
  remove_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/remove-from-cart',
      type: "POST",
      data: {
        'product_id': product_id,
      },
      success: function(data) {
        remove_btn.css('color', '');
        remove_btn.attr('onclick', 'add_to_cart(' + product_id +')');
        remove_btn.attr('id', 'add_to_cart_' + product_id);
        if ( remove_btn.text().search('Remove from Cart') != -1 ) {
          remove_btn.text('Add to Cart');
          remove_btn.css('color', '');
          remove_btn.removeClass('is-light');
          remove_btn.addClass('is-dark');
        }
        $('.cart_item_'+ product_id).css('display', 'none');
        cart_count = $('#cart_count').text();
        $('#cart_count').text(parseInt(cart_count) - 1);
        remove_btn.removeAttr('disabled');
      },
      error: function (data) {
        remove_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
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
        add_btn.attr('onclick', 'remove_from_wish_list(' + product_id +')');
        add_btn.attr('id', 'remove_from_wish_list_' + product_id);
        if ( add_btn.text().search('Add to Wish List') != -1 ) {
          add_btn.text('Remove from Wish List');
          add_btn.css('color', '');
          add_btn.removeClass('is-dark');
          add_btn.addClass('is-light');
        }
        wish_list_count = $('#wish_list_count').text();
        $('#wish_list_count').text(parseInt(wish_list_count) + 1);
        add_btn.removeAttr('disabled');
      },
      error: function (data) {
        add_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
      },
    });
}

function remove_from_wish_list(product_id){
  var remove_btn = $('#remove_from_wish_list_' + product_id);
  remove_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/remove-from-wish-list',
      type: "POST",
      data: {
        'product_id': product_id,
      },
      success: function(data) {
        remove_btn.css('color', '');
        remove_btn.attr('onclick', 'add_to_wish_list(' + product_id +')');
        remove_btn.attr('id', 'add_to_wish_list_' + product_id);
        $('.wish_item_'+ product_id).css('display', 'none');
        if ( remove_btn.text().search('Remove from Wish List') != -1 ) {
          remove_btn.text('Add to Wish List');
          remove_btn.css('color', '');
          remove_btn.removeClass('is-light');
          remove_btn.addClass('is-dark');
        }
        wish_list_count = $('#wish_list_count').text();
        $('#wish_list_count').text(parseInt(wish_list_count) - 1);
        remove_btn.removeAttr('disabled');
      },
      error: function (data) {
        remove_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
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
        url: '/change-cart-item-qty',
        type: "POST",
        data: {
          'product_id': product_id, 'new_quantity': parseInt(qty)
        },
        success: function(data) {
          	qty_btn.removeAttr('disabled');
            alert('Success: '+ data['msg']);
          	window.location.reload();
        },
        error: function (data) {
			qty_btn.removeAttr('disabled');
			alert('Error: '+ data['responseJSON']['msg']);
        },
      });
  }
}

function remove_shipping_address(shipping_id){
  var remove_btn = $('#remove_shipping_address_' + shipping_id);
  remove_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/remove-shipping-address',
      type: "POST",
      data: {
        'shipping_id': shipping_id,
      },
      success: function(data) {
        $('.shipping_address_'+ shipping_id).css('display', 'none');
        remove_btn.removeAttr('disabled');
      },
      error: function (data) {
        remove_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
      },
    });
}

function cancel_order(order_ref){
  var cancel_btn = $('#cancel_order_' + order_ref);
  var cancel_order_reason = $('#cancel_order_reason').val();
  cancel_btn.attr('disabled', 'disabled');
  $.ajax({
      url: '/cancel-order',
      type: "POST",
      data: {
        'order_ref': order_ref, 'reason': cancel_order_reason
      },
      success: function(data) {
        cancel_btn.removeAttr('disabled');
        $(".modal").removeClass("is-active");
        window.location.reload();
      },
      error: function (data) {
        cancel_btn.removeAttr('disabled');
        alert('Error: '+ data['responseJSON']['msg']);
      },
    });
}

function confirm_delivery(order_ref){
  var confirm_btn = $('#confirm_order_' + order_ref);
  if (confirm("Are you sure you want to confirm the delivery?") == true){
  confirm_btn.attr('disabled', 'disabled');
  confirm_btn.text('Confirming Delivery..');
  $.ajax({
      url: '/confirm-delivery',
      type: "POST",
      data: {
        'order_ref': order_ref
      },
      success: function(data) {
        confirm_btn.removeAttr('disabled');
        window.location.reload();
      },
      error: function (data) {
        confirm_btn.removeAttr('disabled');
        confirm_btn.text('Confirm Delivery');
        alert('Error: '+ data['responseJSON']['msg']);
      },
    });
  }
  else {}
}