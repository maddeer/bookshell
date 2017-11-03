$(document).ready(function(){

moment.locale('ru');
//var ahmet = moment("25/04/2012","DD/MM/YYYY").year();
var date = new Date();
bugun = moment(date).format("DD/MM/YYYY");

      var date_input=$('input[name="date"]'); //our date input has the name "date"
      var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
      var options={
        //startDate: '+1d',
        //endDate: '+0d',
        container: container,
        todayHighlight: true,
        autoclose: true,
        format: 'dd/mm/yyyy',
        language: 'tr',
        //defaultDate: moment().subtract(15, 'days')
        //setStartDate : "<DATETIME STRING HERE>"
      };
      date_input.val(bugun);
      date_input.datepicker(options).on('focus', function(date_input){
     $("h3").html("focus event");      
      }); ;
      
      
 date_input.change(function () {
    var deger = $(this).val();
  });      
      
$('.input-group').find('.glyphicon-calendar').on('click', function(){
//date_input.trigger('focus');
//date_input.datepicker('show');
 //$("h3").html("event : click");

if( !date_input.data('datepicker').picker.is(":visible"))
{
       date_input.trigger('focus');
    $("h3").html("Ok"); 
 
    //$('.input-group').find('.glyphicon-calendar').blur();
    //date_input.trigger('blur');
    //$("h3").html("görünür");    
} else {
}


});      

$('.set-deleted').bind('click', function(event){
	event.preventDefault();
	var targetid='#div'+event.target.id; 
	$.getJSON('/delete-chapter/'+event.target.id, function(data){ 
		console.log(data['deleted']);
		if ( data['deleted'] == 1 ){
			$(targetid).addClass('deleted');
			if ( $('input[type=radio][name=ShowDeleted]:checked').val() == 'hide' ){
				$(targetid).hide();
			}
		}
		else if ( data['deleted'] == 0 ){
			$(targetid).removeClass('deleted').show();
		};
	});
});

$('input[type=radio][name=ShowDeleted]').change(function() {
    if (this.value == 'show') {
		$( ".deleted" ).show();
    }
    else if (this.value == 'hide') {
		$( ".deleted" ).hide();
    }
});
$( ".deleted" ).hide();

});
