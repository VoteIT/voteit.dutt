if(deform) {
    function update_choices_lefts(tag) {
        parent = $(tag).parents('form');
        max = parent.find('input[name=max]').val()
        var count = parent.find('input:checked').length;
        parent.find('.dutt_count').text(max - count);
    }
    
    $('input:checkbox.dutt_proposals').live('click', function(event) {
        update_choices_lefts(this);
    });
    $(document).ready(function (){
        $('ul.duttWidget').each(function () {
            update_choices_lefts(this);
        });
    });
}

