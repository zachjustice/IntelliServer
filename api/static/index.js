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
        url: "api/v2.0/entities/" + entity_pk + "/meal_plans?num_days=3&include_recipes=true",
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
    var i = 0;

    for(var meal_type of meal_types)
    {
        // take the first meal since we requested one day of meal plans
        var meal = meal_plans['lunch'][i];
        console.log('meal');
        console.log(meal);
        i++;
        display_recipe(meal, meal_type);
        $('.' + meal_type + '_button').css('background-color', '#f15c48');
    }

    hide_loading_screen();
}

function show_loading_screen() {
    $('#loading_container').css('visibility', 'visible');
    $('#meal_plan_container').css('visibility', 'hidden');
    $('#rating').css('visibility', 'hidden');
    $('#graph').css('visibility', 'hidden');
}

function hide_loading_screen() {
    $('#loading_container').css('visibility', 'hidden');
    $('#meal_plan_container').css('visibility', 'visible');
    $('#rating').css('visibility', 'visible');
    $('#graph').css('visibility', 'visible');
}

function display_recipe(recipe, meal_type) {
    console.log("RECIPE");
    console.log(recipe);
    $('#' + meal_type + '_image').attr('src', recipe['image_url']);
    $('#' + meal_type + '_name').text(recipe['name']);

    $('#' + meal_type +   '_rate_up').data("rating", 1);
    $('#' + meal_type + '_rate_down').data("rating", 0);

    $('#' + meal_type +   '_rate_up').data("recipe_pk", recipe['recipe_pk']);
    $('#' + meal_type + '_rate_down').data("recipe_pk", recipe['recipe_pk']);

    $('.' + meal_type + '_button').prop('disabled', false);
    $('.' + meal_type + '_button').unbind('click');
    $('.' + meal_type + '_button').click( function() {
        $('.' + meal_type + '_button').prop('disabled', true);
        $('.' + meal_type + '_button').css('background-color', '#ddd');

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
            graph(cumulative_ratings);
        }
    });
}

function rate_recipe(recipe_pk, rating) {
    $.ajax({
        url: "api/v2.0/entities/" + entity_pk + "/recipes/" + recipe_pk + "?rating=" + rating,
        method: "POST",
        password: "super123",
        username: "test",
    })
    .done( function (response) {
        console.log("Received recipe rating response");
        console.log(response);
    });
}

function graph(data) {
    // define dimensions of graph
    var m = [80, 80, 80, 80]; // margins
    var w = 1000 - m[1] - m[3]; // width
    var h = 400 - m[0] - m[2]; // height

    // X scale will fit all values from data[] within pixels 0-w
    var x = d3.scale.linear().domain([0, data.length]).range([0, w]);
    // Y scale will fit values from 0-10 within pixels h-0 (Note the inverted domain for the y-scale: bigger is up!)
    var y = d3.scale.linear().domain([0, 1.0]).range([h, 0]);
    // automatically determining max range can work something like this
    // var y = d3.scale.linear().domain([0, d3.max(data)]).range([h, 0]);

    // create a line function that can convert data[] into x and y points
    var line = d3.svg.line()
        // assign the X function to plot our line as we wish
        .x(function(d,i) {
            // verbose logging to show what's actually being done
            console.log('Plotting X value for data point: ' + d + ' using index: ' + i + ' to be at: ' + x(i) + ' using our xScale.');
            // return the X coordinate where we want to plot this datapoint
            return x(i);
        })
        .y(function(d) {
            // verbose logging to show what's actually being done
            console.log('Plotting Y value for data point: ' + d + ' to be at: ' + y(d) + " using our yScale.");
            // return the Y coordinate where we want to plot this datapoint
            return y(d);
        })

        // Add an SVG element with the desired dimensions and margin.
        var graph = d3.select("#graph").append("svg:svg")
              .attr("width", w + m[1] + m[3])
              .attr("height", h + m[0] + m[2])
            .append("svg:g")
              .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

        // create xAxis
        var xAxis = d3.svg.axis().scale(x).ticks(data.length).tickFormat(function(d) { return d + 1; })
        // Add the x-axis.
        graph.append("svg:g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + h + ")")
              .call(xAxis);


        // create left yAxis
        var yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");
        // Add the y-axis to the left
        graph.append("svg:g")
              .attr("class", "y axis")
              //.attr("transform", "translate(-25,0)")
              .call(yAxisLeft);

        // Add the line by appending an svg:path element with the data line we created above
        // do this AFTER the axes above so that the line is above the tick-lines
        graph.append("svg:path").attr("d", line(data));
}
