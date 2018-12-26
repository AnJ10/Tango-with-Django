$('.likes').click( function() {
	
	let catid;
	catid = $(this).attr('data-catid');
	like_id = $(this).attr('like-id');
	$.get('/rango/like/', {category_id : catid, like_id : like_id }, function(data) {
		
	//	alert(data);
		$('#like_count').html(data["likes"]);
		$('.likes').attr('like-id', data["like_id_update"]);
		$('.likes').html(data["button_update"]);

	});
	
});

$('#suggestion').keyup( function() {

	let suggestion = $(this).val();
	$.get('/rango/suggest/', {suggestion:suggestion}, function(data) {
		$('#cats').html(data);	

	});
});

$('.rango-add').click( function() {
	let url = $(this).attr('url');
	let title = $(this).attr('title');
	let category_id = $(this).attr('category_id');
	let add_id = $(this).attr('add-id');
	let me = $(this);
	$.get('/rango/button_add_page/', { url:url, title:title, category_id:category_id, add_id:add_id }, function(data) {
		$('#pages').html(data);
		if (add_id == 'add') {
			me.html("Remove");
			me.attr('add-id', "remove");
		}
		else {
			me.html("Add");
			me.attr('add-id', "add");
		}

	});
});

/*
$('.rango-add').click( function() {
	alert('Here');
	let url = $(this).attr('url');
	let title = $(this).attr('title');
	let category_id = $(this).attr('category_id');
	let add_id = $(this).attr('add-id');
	let me = $(this);
	alert(url);
	$.get('/rango/button_add_page/', { url:url, title:title, category_id:category_id, add_id:add_id }, function(data) {
		$('#pages').html(data.response);
		me.attr('add-id', add_id_update );
		me.html(button_update);

	});

});*/