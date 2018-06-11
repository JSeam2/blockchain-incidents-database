(document).ready(function(){
  $('[data-toggle="popover"]').popover();   
});

$('html').on('mouseup', function(e) {
  if(!$(e.target).closest('.popover').length) {
  	$('.popover').each(function(){
			$(this.previousSibling).popover('hide');
		});
  }
});

