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
        $('.box').css('display', 'none');
        $('#checkout_btn').css('display', 'none');
        // empty_btn.removeAttr('disabled');
        empty_btn.css('display', 'none');
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty cart');
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
        $('.box').css('display', 'none');
        empty_btn.css('display', 'none');
      },
      error: function (data) {
        empty_btn.removeAttr('disabled');
        empty_btn.text('Empty Wish List');
      },
    });
}

function remove_from_cart(item_id, qty){
  var remove_btn = $('#remove_from_cart' + item_id);
  console.log(remove_btn);
  remove_btn.attr('disabled', 'disabled');
  remove_btn.text('Removing...');
  $.ajax({
      url: '/remove-from-cart',
      type: "POST",
      data: {
        'item_id': item_id, 'qty': qty
      },
      success: function(data) {
        remove_btn.parent().parent().parent().parent().css('display', 'none');

        $('#items_total').text(parseInt($('#items_total').text()) - qty);
        if(parseInt($('#items_total').text()) <= 0){
            $('#subtotal').text('0');
        }else{
          var t = $('#subtotal').text().replace(',', '');
          t = t.replace(',', '');
          t = t.replace(',', '');
          t = t.replace(',', '');
          $('#subtotal').text(parseInt(t) - data['cost'] * qty);
        }

        remove_btn.removeAttr('disabled');
        remove_btn.text('Remove');
      },
      error: function (data) {
        remove_btn.removeAttr('disabled');
        remove_btn.text('Remove');
      },
    });
}

function add_to_cart(item_id){
  var add_btn = $('#add_to_cart' + item_id);
  var qty_btn = $('#quantity'+ item_id);
  add_btn.attr('disabled', 'disabled');
  add_btn.text('Adding...');
  $.ajax({
      url: '/add-to-cart',
      type: "POST",
      data: {
        'item_id': item_id, 'quantity': parseInt($('#quantity'+item_id).val()),
      },
      success: function(data) {
        add_btn.text('Added');
        add_btn.addClass('btn-danger');
        qty_btn.attr('disabled', 'disabled');
      },
      error: function (data) {
        add_btn.removeAttr('disabled');
        add_btn.text('Add to cart');
      },
    });
}


function change_qty (item_id, ori_qty){
  var qty_btn = $('#change_qty' + item_id);
  var qty = $('#qty' + item_id).val();
  qty_btn.attr('disabled', 'disabled');
  if(ori_qty == qty){
    qty_btn.removeAttr('disabled');
    alert('This quantity is still the same');
  }else{
    $.ajax({
        url: '/change-qty',
        type: "POST",
        data: {
          'item_id': item_id, 'n_qty': qty
        },
        success: function(data) {
          qty_btn.removeAttr('disabled');
          if(data['status'] == 'success'){

            $('#items_total').text(parseInt($('#items_total').text()) - data['f_qty']);
            $('#items_total').text(parseInt($('#items_total').text()) + parseInt(qty));

            if(parseInt($('#items_total').text()) <= 0){
                $('#subtotal').text('0');
            }else{
              var t = $('#subtotal').text();
              t = t.replace(',', '');
              t = t.replace(',', '');
              t = t.replace(',', '');
              $('#subtotal').text(parseInt(t) - (data['cost'] * data['f_qty']));
              $('#subtotal').text(parseInt(t) + (data['cost'] * parseInt(qty)));

              $('#qtytxt' + item_id).text(qty);
            }
          }
          else{
            alert('Error: '+ data['message']);
            qty_btn.removeAttr('disabled');
          }
        },
        error: function (data) {
          qty_btn.removeAttr('disabled');
        },
      });
  }
}
