+function ($) {
  newRecipe = function() {
    $(".new_recipe").click(function(e){
      e.preventDefault()

      delete localStorage["crt_recipe_form"]
      var country = $(this).attr("data-country")
      localStorage["crt_recipe_form"] = JSON.stringify({"country": country})
      $("#recipe_form").find("input, textarea").val("")
      $("#recipe_form #country").val(country)
      setUUID()

      setImageData("", "", "")
    });
  }

  loadRecipe = function() {
    $(".load_recipe").click(function(){
      var uuid = $(this).attr("data-id")

      $.get("/getRecipe/"+uuid, function(data){
        localStorage["crt_recipe_form"] = data
        loadForm()
      });

    });
  }


  $("#recipe_form").change(function() {saveForm()});
  newRecipe()
  loadRecipe()

  $("#recipe_form #title").change(function(){
    if ($("#recipe_form #image_desc").val().length == 0) {
      $("#recipe_form #image_desc").val($(this).val())
    }

  })

  $(window).bind('keydown', function(event) {
    if (event.ctrlKey || event.metaKey) {
        switch (String.fromCharCode(event.which).toLowerCase()) {
        case 's':
            event.preventDefault();
            saveForm()
            break;
        }
    }
});

  $("#image_uri").change(function(){
    var image_url = $("#image_uri").val()
    var image_source_uri = $("#image_source_uri").val()
    var image_desc = $("#image_desc").val()

    setImageData(image_url, image_source_uri, image_desc)

    saveForm()
  });

  $("#new_country_save").click(function(){
    var country = $("#modal_new_country").val()
    var book_uuid = $("#master_book_uuid").val()

    $.get("/newCountry/"+book_uuid+"/"+country, function(data){
      var container = $(".country-container").first().clone()

      $(container).find(".recipe-label").each(function(){$(this).remove()})
      $(container).attr("id", "country-"+sc(country)).find(".country_name").html(country)
      $(container).find(".new_recipe").attr("data-country", country)
      $(".country-container").last().after(container)
      newRecipe()
    });
  });



  $(".delete_recipe").click(function(){
    if (confirm("Do you really want to delete this recipe?")) {
      var elem = $(this)
      $.get("/deleteRecipe/"+$(this).attr("data-id"), function(data){
        $(elem).parent().remove()
      });
    }
  });

  sc = function(country) {
    return country.replace(" ", "-")
  }

  addRecipe = function(data) {
    var recipe_label = $("#country-"+sc(data["country"])+".recipe-label").last().clone()
    if ($(recipe_label).html() == undefined) {
      recipe_label = $('<div class="text-muted recipe-label"><a href="#" class="load_recipe" data-id="'+data["uuid"]+'">'+data["title"]+'</a> <span class="delete_recipe" data-id="'+data["uuid"]+'">x</span></div>')
    $("#country-"+sc(data["country"])+" .new_recipe").before(recipe_label)
    } else {
      $(recipe_label).find("a").attr("data-id", data["uuid"]).html(data["title"])
    $("#country-"+sc(data["country"])+" .recipe-label").last().after(recipe_label)
    }
    loadRecipe()
  }

  updateRecipe = function(data) {
    $("#country-"+sc(data["country"])+" .recipe-label a[data-id='"+data["uuid"]+"']").html(data["title"])
  }

  setImageData = function(image_url, image_source_uri, image_desc) {
    $("#recipe_form #image #image_uri").val(image_url)
    $("#recipe_form #image #image_uri_elem").attr("src", image_url)
    $("#recipe_form #image #image_source_uri").val(image_source_uri)
    $("#recipe_form #image #image_desc").val(image_desc)
    $("#recipe_form #image #image_desc_elem").html(image_desc)
    $("#recipe_form #image").css("display", "block")
  }

  saveForm = function() {
    localStorage["crt_recipe_form"] = getFormData("#recipe_form .recipe_data")
    //$.post("/saveRecipe", JSON.stringify(localStorage["crt_recipe_form"]))

    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/saveRecipe",
      data: JSON.stringify(localStorage["crt_recipe_form"]),
      dataType: "json",

    }).done(function(data){
      if (data.was_new) {
        addRecipe(JSON.parse(data.recipe))
      } else {
        updateRecipe(JSON.parse(data.recipe))
      }
      $("#saved_msg").fadeIn(500).fadeOut(500).fadeIn(500).fadeOut(500).fadeIn(500).fadeOut(500);
    }).fail(function(data){alert(JSON.stringify(data))});
  }

  loadForm = function(id) {
    if (localStorage["crt_recipe_form"] != undefined) {
        var data = JSON.parse(localStorage["crt_recipe_form"]);
        var obj = $(id);
        for(var id in data) {
          //alert(id+" "+data[id])
          if (id == "image") {
            loadImage(data[id])
          } else if (id == "ingredients") {
            loadIngredients(data[id])
          } else {
            $("#recipe_form #"+id).val(data[id])
          }
        }

        setUUID()
    }

    return {}
  }

  setUUID = function() {
    if ($("#recipe_form #uuid").val().length == 0) {
      $.get("/getUUID", function(data){
        $("#recipe_form #uuid").val(data)
      });
    }
  }

  loadImage = function(data) {
    setImageData(data["uri"], data["source_uri"], data["description"])
  }

  loadIngredients = function(data) {

    $("#recipe_form #ingredients").val(data.join("\n"));
  }

  getText = function(master, id) {
    id = master+" "+id
    return $(id).val();
  }

  getImage = function(master, id) {
    id = master+" "+id
    return {"uri": $(id+" #image_uri").val(), "source_uri": $(id+" #image_source_uri").val(), "description": $(id+" #image_desc").val()};
  }

  getIngredients = function(master, id) {
    id = master+" "+id
    var list = $(id).val().trim().split("\n")

    return list
  }

  getFormData = function(id){
    var obj = $(id)

    var data={}
    data["book_uuid"] = getText("", "#master_book_uuid")
    data["country"] = getText("#recipe_form", "#country")
    data["uuid"] = getText("#recipe_form", "#uuid")
    data["title"] = getText("#recipe_form", "#title")
    data["description"] = getText("#recipe_form", "#description")
    data["image"] = getImage("#recipe_form", "#image")
    data["serving"] = getText("#recipe_form", "#serving")
    data["preparing_time"] = getText("#recipe_form", "#preparing_time")
    data["ingredients"] = getIngredients("#recipe_form", "#ingredients")
    data["directions"] = getText("#recipe_form", "#directions")


    return JSON.stringify(data)
  }

  loadForm("#recipe_form .recipe_data")
}(jQuery);
