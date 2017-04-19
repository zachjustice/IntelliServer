"use strict";

var entity_pk = 8;
var ratings = [];
var rated_positive = 0;
var cumulative_ratings = []
var running_ratings = []

$(init);

function init() {
    get_meal_plans(entity_pk);
}

function get_meal_plans(entity_pk) {
    console.log("GET MEAL PLAN");
    show_loading_screen();
    $.ajax({
        url: "api/v2.0/entities/" + entity_pk + "/meal_plans?num_days=1&include_recipes=true",
        method: "POST",
        password: "super123",
        username: "test"
    })
    .done( display_meal_plans )
}

function display_meal_plans(meal_plans) {
    console.log("Meal Plans");
    console.log(meal_plans);
    var meal_types = ['breakfast', 'lunch', 'dinner'];

    for(var meal_type of meal_types)
    {
        var meal = meal_plans[meal_type];
        display_recipe(meal, meal_type);
    }

    hide_loading_screen();
}

function show_loading_screen() {
    $('#loading_container').show();
    $('#meal_plan_container').hide();
}

function hide_loading_screen() {
    $('#loading_container').hide();
    $('#meal_plan_container').show();
}

function display_recipe(recipe, meal_type) {
    console.log("RECIPE");
    console.log(recipe);
    $('#' + meal_type + '_image').attr('src', recipe['image_url']);
    $('#' + meal_type + '_name').text(recipe['name']);

    $('#' + meal_type +   '_rate_up').data("rating", 1);
    $('#' + meal_type + '_rate_down').data("rating", -1);

    $('#' + meal_type +   '_rate_up').data("recipe_pk", recipe['recipe_pk']);
    $('#' + meal_type + '_rate_down').data("recipe_pk", recipe['recipe_pk']);

    $('.' + meal_type + '_button').prop('disabled', false);
    $('.' + meal_type + '_button').unbind('click');
    $('.' + meal_type + '_button').click( function() {
        $('.' + meal_type + '_button').prop('disabled', true);

        var recipe_pk = $(this).data("recipe_pk");
        var rating    = $(this).data("rating");

        console.log("CLICKED RATE BUTTON: " + rating + " " + recipe_pk);
        rate_recipe(recipe_pk, rating);
        ratings.push({"recipe_pk": recipe_pk, "rating": rating});

        if(rating == 1) {
            rated_positive++;
        }

        var percentage_correct = rated_positive / ratings.length
        var percentage_last_six = 0;
        var num_last_six = 0;

        for (var i = ratings.length - 1; i >= 0 && i > ratings.length - 7; i--) {
            if(ratings[i]['rating'] == 1) {
                num_last_six++;
            }
        }

        if(ratings.length < 6)
        {
            percentage_last_six = num_last_six / ratings.length;
        } else {
            percentage_last_six = num_last_six / 6;
        }

        $('#cumulative_rating').text(percentage_correct);
        $('#running_rating').text(percentage_last_six);

        cumulative_ratings.push(percentage_correct);
        running_ratings.push(percentage_last_six);

        if(ratings.length > 0 && ratings.length % 3 == 0)
        {
            get_meal_plans(entity_pk);
        }
    });
}

function rate_recipe(recipe_pk, rating) {
    if(!recipe_pk || !rating) {
        console.log("Invalid argument. recipe_pk: " + recipe_pk + ", rating: " + rating);
        return;
    }

    $.ajax({
        url: "api/v2.0/entities/" + entity_pk + "/recipes/" + recipe_pk,
        method: "POST",
        password: "super123",
        username: "test",
        data: {"rating": rating, "recipe_pk": recipe_pk}
    })
    .done( function (response) {
        console.log("Received recipe rating response");
        console.log(response);
    });
}
