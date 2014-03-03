// KineticJS JavaScript Framework http://www.kineticjs.com/ Copyright 2013, Eric Rowell. Licensed under the MIT license.

// Get jsons from the server
var images_json_text = getJSON('images.json');
var objects_json = JSON.parse(getJSON('objects.json'));
var legends_json = JSON.parse(getJSON('legends.json'));
var texts_json = JSON.parse(getJSON('texts.json'));

// Create stage and everything in it from json
var stage = Kinetic.Node.create(images_json_text, 'container');

// Scale stage to window size
//stage.setWidth(window.innerWidth);
//stage.setHeight(window.innerHeight);

// Define variables from stage for easier use

// Texts & layers
var monologue = stage.get('#monologue')[0];
var speech_bubble = stage.get('#speech_bubble')[0];
var interaction_text = stage.get('#interaction_text')[0];

var start_layer = stage.get("#start_layer")[0];
var intro_layer = stage.get("#intro_layer")[0];
var outro_layer = stage.get("#outro_layer")[0];
var end_layer = stage.get("#end_layer")[0];

var background_layer = stage.get("#background_layer")[0];

var inventory_layer = stage.get('#inventory_layer')[0];
var inventory_bar_layer = stage.get("#inventory_bar_layer")[0];
var character_layer = stage.get('#character_layer')[0];
var text_layer = stage.get('#text_layer')[0];
var fade_layer = stage.get("#fade_layer")[0];

// Character frames
var speak_1 = stage.get('#character_speak_1')[0];
var speak_2 = stage.get('#character_speak_2')[0];
var idle_1 = stage.get('#character_idle_1')[0];
var idle_2 = stage.get('#character_idle_2')[0];
var panic = stage.get('#character_panic')[0];

// Scale background and UI elements
stage.get("#black_screen")[0].setSize(stage.getWidth(), stage.getHeight());
stage.get("#inventory_bar")[0].setY(stage.getHeight() - 100);
stage.get("#inventory_bar")[0].setWidth(stage.getWidth());

// Make a json object from the json string
var images_json = stage.toObject();

// Variable for saving the current room (for changing backgrounds and object layers)
var current_background = 'start_layer';

// The amount of rewards found
var rewards = 0;

// The amount of items in the inventory
var inventory_items = 0;
// Offset from left for drawing inventory items starting from proper position
var offsetFromLeft = 50;
// How many items the inventory can show at a time (7 with current settings)
var inventory_max = 7;
// The item number where the shown items start from
// (how many items from the beginning are not shown)
var inventory_index = 0;

// Timeout event for showing monologue animation for certain duration
var monologue_timeout;

// Temporary location for inventory items if they need to be moved back to the location because of invalid interaction
var x;
var y;

// For limiting the amount of intersection checks
var delayEnabled = false;

// For limiting the speed of inventory browsing when dragging an item
var dragDelay = 500;
var dragDelayEnabled = false;

// For checking whether player has selected their jersey number
var number_selected = false;

// Music
// Different browsers and different browser versions support different formats. MP3 should work with in all the major
// browsers in current versions.
var current_music;
var current_music_source;

// The item dragged from the inventory
var dragged_item;

// Intersection target (object below dragged item)
var target;

// Animation for fading the screen
var fade = new Kinetic.Tween({
	node : fade_layer,
	duration : 0.6,
	opacity : 1
});

var wakeup = new Kinetic.Tween({
	node : fade_layer,
	duration : 3,
	opacity : 1
});

// Speak animation
var speak_1_animation = new Kinetic.Tween({
	node : speak_1,
	duration : 0.3,
	onFinish : function() {
		speak_1.hide();
		speak_2.show();
		speak_1_animation.reset();
		speak_2_animation.play();
	}
});
var speak_2_animation = new Kinetic.Tween({
	node : speak_2,
	duration : 0.3,
	onFinish : function() {
		speak_1.show();
		speak_2.hide();
		speak_2_animation.reset();
		speak_1_animation.play();
	}
});
// Character's idle animation
var idle_1_animation = new Kinetic.Tween({
	node : idle_1,
	duration : 8.7,
	onFinish : function() {
		idle_1.hide();
		idle_2.show();
		idle_1_animation.reset();
		idle_2_animation.play();
	}
});
var idle_2_animation = new Kinetic.Tween({
	node : idle_2,
	duration : 0.2,
	onFinish : function() {
		idle_1.show();
		idle_2.hide();
		idle_2_animation.reset();
		idle_1_animation.play();
	}
});

function create_animation (object) {
	var attrs = object.getAttr("animation");
	var animation = new Kinetic.Tween({
    	node: object,
        x: attrs.x ? object.getX() + attrs.x : object.getX(),
        y: attrs.y ? object.getY() + attrs.y : object.getY(),
        width: attrs.width ? object.getWidth() - 15 : object.getWidth(),
        easing: Kinetic.Easings.EaseInOut,
        duration: attrs.duration,
        
		onFinish: function() {
			animation.reverse();
			setTimeout(function() {
            	animation.play();
            }, attrs.duration * 1000);
		}
    });
    
    // TODO: Playing everything at once can end up being laggy
    animation.play();
}

// Creating all image objects from json file based on their attributes
for (var i = 0; i < images_json.children.length; i++) {
	for (var j = 0; j < images_json.children[i].children.length; j++) {
		if (images_json.children[i].children[j].className == 'Image') {
			createObject(images_json.children[i].children[j].attrs);
            
            if (images_json.children[i].children[j].attrs.animated === true)
            	create_animation(stage.get('#'+images_json.children[i].children[j].attrs.id)[0]);
		}
	}
}

// On window load we create image hit regions for our items on object layers
// Some items ended up being excluded from this
window.onload = function() {
    // Loop backgrounds to create item hit regions and register mouseup event
    background_layer.getChildren().each(function(o) {        
        object_layer = stage.get('#'+o.attrs.objects)[0];
        
        if (object_layer != undefined) {
            object_layer.getChildren().each(function(shape, i) {
                if (shape.getAttr('category') != 'secret' && shape.className == 'Image') {
                    shape.createImageHitRegion(function() {
                    });
                }
            });
            
            object_layer.on('mouseup touchend', function(event) {
                interact(event);
            });
            
            // Current layer for hit region purposes in different rooms
            if (object_layer.getAttr('start') == 'true') {
                current_layer = object_layer;
            }
        }
    });
    
	stage.draw();
	idle_1_animation.play();
}

stage.get('#begining')[0].on('tap click', function(event) {
	stage.get('#begining')[0].hide();
	inventory_bar_layer.show();
	character_layer.show();
	background_layer.show();
	stage.draw();
	play_music('start_layer');
});

stage.get('#start_game')[0].on('tap click', function(event) {
    play_sequence("intro");
});

// Listener and showing of credits on the start screen
stage.get('#start_credits')[0].on('tap click', function(event) {
	event = event.targetNode;
	setMonologue(event.getAttr('id'));
});

/*
Play music
string id - object ID from JSON with "music":"file name" attribute
*/
function play_music(id) {
    var data = objects_json[id];
    
    // ID and music found from JSON?
    if (!data || !data.music) {
        if (current_music) {
            current_music.pause();
            current_music = null;
        }
        return;
    }
    
    // If not already playing music or old/new songs are different
    if (!current_music || current_music_source != data.music) {
        if (current_music)
            current_music.pause();
        
        current_music = new Audio(data.music);
        data.music_loop === false ? current_music.loop = false : current_music.loop = true;
        
	    current_music.play();
	    
        current_music_source = data.music;
	}
}

/*
Plays a sequence defined in JSON
string sequence - the sequence ID from JSON
string post_sequence_image - the image displayed after sequence
*/
function play_sequence(sequence) {
	// Animation cycle for proper fading and drawing order
	fade_layer.moveUp();
	fade_layer.show();
	fade.play();
	
	current_music.pause();
	
	var sequence_layer = stage.get("#"+sequence)[0];
    var object = objects_json[sequence_layer.getAttr('object_name')];
    
    sequence_layer.show();
    
    var delay = 700;
    var sequence_counter = 0;
    var images_total = 0;
    
    for (var i in object.images) {
    	images_total++;
        var image = stage.get('#' + object.images[i].id)[0];
        
    	(function(i, image) {
            setTimeout(function() {
                fade_layer.show();
                fade.play();
                
                if (sequence_counter == 0)
                    play_music(sequence);
                    
                character_layer.hide();
                inventory_bar_layer.hide();
                
                image.show();
                
                var image_fade = object.images[i].do_fade;
                if (image_fade === true) {
                    setTimeout(function() {
                        fade.reverse();
                        stage.draw();
                        setTimeout('fade_layer.hide();', 700);
                    }, 700);
                }
                // Immediately revert fade layer
                else {
                    fade.reverse();
                    stage.draw();
                    fade_layer.hide();
                }
                
                sequence_counter += 1;
                
                // Last image in the sequence
                if (images_total == sequence_counter) {
                    fade_layer.show();
                    wakeup.finish();
                    
                    setTimeout(function() {
                        current_music.pause();
                        wakeup.reverse();
                        intro_layer.hide();
                        
                        stage.get("#"+object.transition)[0].show();
                        current_layer.show();
                        inventory_bar_layer.show();
                        character_layer.show();
                        
                        stage.draw();
                        setTimeout(function() {
                            fade_layer.hide();
                            stage.get("#black_screen")[0].setSize(stage.getWidth(), stage.getHeight() - 100);
                            fade_layer.moveDown();
                            setMonologue(sequence, 'end_text');
                            play_music(object.transition);
                        }, 3000);
                    }, 1500);
                    
                    return;
                }
                
            }, delay);
        })(i, image);
        
        delay = delay + object.images[i].show_time;
	};
}

// Developer feature - shortcut menu from the empty menu button for testing purposes
	stage.get('#start_empty')[0].on('tap click', function(event) {
	event = event.targetNode;
	var clone;
    
	clone = stage.get('#oikotie')[0].clone({
		visible : true,
		x : 50
	});
	clone.moveTo(start_layer);
	clone.on('click', function() {current_music.pause();});
    
	clone = stage.get('#oikotie_locker_room2')[0].clone({
		visible : true,
		x : 200
	});
	clone.moveTo(start_layer);
	clone.on('click', function() {
	    current_music.pause();
	    inventoryAdd(stage.get('#poster_withoutglue')[0]);
	    inventoryAdd(stage.get('#airfreshener')[0]);
	    inventoryAdd(stage.get('#cienibang')[0]);
	});
    
    
	/*
	clone = stage.get('#locker_room_1_door_to_wc_open')[0].clone({
		visible : true,
		x : 600
	});
	clone.moveTo(start_layer);
	clone = stage.get('#shower_door_to_locker_room_2_open')[0].clone({
		visible : true
	});
	clone.moveTo(start_layer);
	clone = stage.get('#shower_door_to_locker_room_1')[0].clone({
		x : 330
	});
	clone.moveTo(start_layer);
	*/
	stage.draw();
});

// Mouse up and touch end events (picking up items from the environment
// Start layer for the shortcut developer menu
start_layer.on('mouseup touchend', function(event) {
	interact(event);
});

// Mouse click and tap events (examine items in the inventory)
inventory_layer.on('click tap', function(event) {
	interact(event);
});
// Drag start events
stage.get('Image').on('dragstart', function(event) {
	dragged_item = event.targetNode;
	inventoryDrag(dragged_item);
});
// While dragging events (use item on item or object)
stage.on('dragmove', function(event) {
	dragged_item = event.targetNode;

	if (!delayEnabled) {
		// Setting a small delay to not spam intersection check on every moved pixel
		setDelay(10);

		// Loop through all the items on the current object layer
		for (var i = 0; i < current_layer.children.length; i++) {
			var object = (current_layer.getChildren())[i];
			if (object != undefined) {
				// Break if still intersecting with the same target
				if (target != null && checkIntersection(dragged_item, target)) {
					break;
				}
				// If not, check for a new target
				else if (checkIntersection(dragged_item, object)) {
					if (target != object) {
						target = object;
					}
					break;
					// No target, move on
				} else {
					target = null;
				}
			}
		}
		// If no intersecting targets were found on object layer, check the inventory
		if (target == null) {
			// Loop through all the items on the inventory layer
			for (var i = 0; i < inventory_layer.children.length; i++) {
				var object = (inventory_layer.getChildren())[i];
				if (object != undefined) {
					// Look for intersecting targets
					if (checkIntersection(dragged_item, object)) {
						if (target != object) {
							target = object;
						}
						break;
					} else {
						target = null;
					}
				}
			}
		}
                // Next, check the inventory_bar_layer, if the item is dragged over the inventory arrows
                if (target == null) {
                    var leftArrow = stage.get("#inventory_left_arrow")[0];
                    var rightArrow = stage.get("#inventory_right_arrow")[0];
                    if (!dragDelayEnabled) {
                        if (checkIntersection(dragged_item, leftArrow)) {
                            dragDelayEnabled = true;
                            inventory_index--;
                            redrawInventory();
                            setTimeout('dragDelayEnabled = false;', dragDelay);
                        } else if (checkIntersection(dragged_item, rightArrow)) {
                            dragDelayEnabled = true;
                            inventory_index++;
                            redrawInventory();
                            setTimeout('dragDelayEnabled = false;', dragDelay);
                        } else {
                            target = null;
                        }
                    }
                }
		// If target is found, highlight it and show the interaction text
		if (target != null) {
			current_layer.getChildren().each(function(shape, i) {
				shape.setShadowBlur(0);
			});
			inventory_layer.getChildren().each(function(shape, i) {
				shape.setShadowBlur(0);
			});
			target.setShadowColor('purple');
			target.setShadowOffset(0);
			target.setShadowBlur(20);

			interaction_text.setText(texts_json[target.getAttr('id')].name);
			interaction_text.setX(dragged_item.getX() + (dragged_item.getWidth() / 2));
			interaction_text.setY(dragged_item.getY() - 30);
			interaction_text.setOffset({
				x : interaction_text.getWidth() / 2
			});
                        
			current_layer.draw();
			text_layer.draw();

			// If no target, clear the texts and highlights
		} else {
			current_layer.getChildren().each(function(shape, i) {
				shape.setShadowBlur(0);
			});
			inventory_layer.getChildren().each(function(shape, i) {
				shape.setShadowBlur(0);
			});
			clearText(interaction_text);
			current_layer.draw();
		}
	}
});
// Basic intersection check; checking whether corners of the dragged item are inside the area of the intersecting object
function checkIntersection(dragged_item, target) {
	// If target is visible and of suitable category
	if (target.isVisible() && (target.getAttr('category') != undefined && target.getAttr('category') != 'secret' && target.getAttr('category') != 'transition')) {
		// If horizontally inside
		if (dragged_item.getX() > target.getX() && dragged_item.getX() < (target.getX() + target.getWidth()) || (dragged_item.getX() + dragged_item.getWidth()) > target.getX() && (dragged_item.getX() + dragged_item.getWidth()) < (target.getX() + target.getWidth())) {
			// If vertically inside
			if (dragged_item.getY() > target.getY() && dragged_item.getY() < (target.getY() + target.getHeight()) || (dragged_item.getY() + dragged_item.getHeight()) > target.getY() && (dragged_item.getY() + dragged_item.getHeight()) < (target.getY() + target.getHeight())) {
				return true;
			}
		}
	}
	return false;
}

// Drag end events
stage.get('Image').on('dragend', function(event) {
	var dragged_item = event.targetNode;
    var object = objects_json[dragged_item.getId()]
        
        // Variable for whether the dragged item is destroyed or not
        var destroy = false;
	
	if (target != null)
    	var say_text = texts_json[dragged_item.getId()][target.getId()];
    		
	// If nothing's under the dragged item
	if (target == null) {
		dragged_item.setX(x);
		dragged_item.setY(y);
	}
	// Default text for unassigned item combinations + return item to inventory
	else if (say_text == undefined) {
		dragged_item.setX(x);
		dragged_item.setY(y);
		setMonologue("default");
	}
	// Put something into a container
	else if (target != null && say_text != undefined && target.getAttr('category') == 'container') {
            var object = objects_json[target.getAttr('object_name')];
            
            // Can dragged object unlock locked container?
            if (object.locked === true && object.key == dragged_item.getId()) {
                object.locked = false;
                stage.get('#' + objects_json[target.getAttr('object_name')]['locked_image'])[0].hide();

                if (object.state == "empty")
                    var unlocked = "empty_image";
                else
                    var unlocked = "full_image";

                stage.get('#' + objects_json[target.getAttr('object_name')][unlocked])[0].show();
            }
            // Can dragged object be put into the container
            else if (object.state == 'empty' && object.in == dragged_item.getId()) {
                    object.state = 'full';
                    
                    if (object.in == dragged_item.getId()) {
                        stage.get('#' + objects_json[target.getAttr('object_name')]['empty_image'])[0].hide();
                        stage.get('#' + objects_json[target.getAttr('object_name')]['full_image'])[0].show();

                        // Remove dragged item
                        destroy = true;
                        current_layer.draw();
                    }
            }
            setMonologue(dragged_item.getId(), target.getId());
	}
    // Unlock a door
	else if (target != null && say_text != undefined && target.getAttr('category') == 'door') {
        var object = objects_json[target.getAttr('object_name')];
        
        if (object.locked === true && object.state == 'locked' && object.key == dragged_item.getId()) {
        	object.state = 'open';
            object.locked = false;
            
            stage.get('#' + object.locked_image)[0].hide();
            stage.get('#' + object.open_image)[0].show();
        }
        
        setMonologue(dragged_item.getId(), target.getId());
    }
    // Unblock an obstacle
	else if (target != null && say_text != undefined && target.getAttr('category') == 'obstacle') {
    	var object = objects_json[target.getAttr('object_name')];
        
        if (object.blocking === true && object.trigger == dragged_item.getId()) {
        	var blocked_object = objects_json[object.target];
            
            object.blocking = false;
            blocked_object.blocked = false;
            
            // TODO: What about other objects than door?
            stage.get('#' + blocked_object.blocked_image)[0].hide();
            stage.get('#' + blocked_object.closed_image)[0].show();
            
            // TODO: unblocking_image, merge this with "use item on object"?
            target.destroy();
            var related = target.getAttr("related");
            if (related && related.size != 0) {
                for (var i in related)
                stage.get("#" + related[i])[0].hide();
            }
        }
        setMonologue(dragged_item.getId(), target.getId());
    }
	// Use item on object
	else if (target != null && say_text != undefined && object && object.outcome != undefined && target.getAttr('category') == 'object') {
		setMonologue(dragged_item.getId(), target.getId());
        
		if (objects_json[dragged_item.getId()].trigger == target.getId()) {
			stage.get('#' + objects_json[dragged_item.getId()].outcome)[0].show();
			
            // Items may be consumed when used
            if (dragged_item.getAttr('consume') === true)
                destroy = true;
            else {
                target.destroy();
            }
			
            var related = target.getAttr("related");
			if (related && related.size != 0) {
            	for (var i in related)
            		stage.get("#" + related[i])[0].hide();
			}
		}
	}
	// Use item on item
	else if (target != null && say_text != undefined && object && object.outcome != undefined && target.getAttr('category') == 'usable') {
		setMonologue(dragged_item.getId(), target.getId());
		if (objects_json[dragged_item.getId()].trigger == target.getId()) {
        	
			stage.get('#' + objects_json[dragged_item.getId()].outcome)[0].show();
			
                    inventoryAdd(stage.get('#' + objects_json[dragged_item.getId()].outcome)[0]);
                    destroy = true;
                    inventoryRemove(target);
		}
	}
    // Default for all others
    else {
        setMonologue(dragged_item.getId(), target.getId());
    }
    // Check if dragged item's destroyed, if not, add it to inventory
    if (destroy == false) {
        inventoryAdd(dragged_item);
        redrawInventory();
    } else {
        dragged_item.hide();
	dragged_item.setDraggable(false);
        dragged_item.destroy;
    }
            
    // Clearing the glow effects
    current_layer.getChildren().each(function(shape, i) {
        shape.setShadowBlur(0);
    });
    inventory_layer.getChildren().each(function(shape, i) {
        shape.setShadowBlur(0);
    });
    // Clearing the texts
    clearText(interaction_text);

    // Stopping the talking animation after certain period of time
    clearTimeout(monologue_timeout);
    monologue_timeout = setTimeout('stopTalking()', 3000);

    current_layer.draw();
});
// Stop talking and clear monologue when clicked or touched anywhere on the screen
stage.on('touchstart mousedown', function(event) {
	clearText(monologue);
	stopTalking();
});
// Touch start and mouse down events (save the coordinates before dragging)
inventory_layer.on('touchstart mousedown', function(event) {
	x = event.targetNode.getX();
	y = event.targetNode.getY();
	//clearText(monologue);
});
// Inventory arrow clicking events
inventory_bar_layer.on('click tap', function(event) {
	interact(event);
});
// Interaction between items based on their category
function interact(event) {
	var target = event.targetNode;

	// Pick up an item
	if (target.getAttr('category') == 'item') {
		setMonologue(target.getAttr('id'), 'pickup');
		if (target.getAttr('src2') != undefined) {
			stage.get('#' + target.getAttr('src2'))[0].show();
			inventoryAdd(stage.get('#' + target.getAttr('src2'))[0]);
			target.destroy();
		} else {
			inventoryAdd(target);
		}
		current_layer.draw();

		// To prevent multiple events happening at the same time
		event.cancelBubble = true;
		// Pick up a secret item
	} else if (target.getAttr('category') == 'secret') {
		setMonologue(target.getAttr('id'), 'pickup');
                var rewardID = target.getAttr('reward');
                inventoryAdd(stage.get('#'+rewardID)[0]);
                stage.get('#'+rewardID)[0].show();
                rewards++;
                target.destroy();
		current_layer.draw();

		// To prevent multiple events happening at the same time
		event.cancelBubble = true;
	}
	// Print examine texts for items, rewards, obstacles and objects
	else if (target.getAttr('category') == 'object' || target.getAttr('category') == 'usable' || target.getAttr('category') == 'reward' || target.getAttr('category') == 'obstacle') {
		setMonologue(target.getAttr('id'));
	}
    // Take an item out of a container
	else if (target.getAttr('category') == 'container') {
		var object = objects_json[target.getAttr('object_name')];
        
        if (object.locked === false) {
        	if (object.state == 'full') {
        		object.state = 'empty';
        
        		stage.get('#' + objects_json[target.getAttr('object_name')]['full_image'])[0].hide();
        		stage.get('#' + objects_json[target.getAttr('object_name')]['empty_image'])[0].show();
        
                // Show and add the added inventory item
        		var new_item = stage.get('#' + object.out)[0];
				new_item.show();
				inventoryAdd(new_item);
        
        		current_layer.draw();
            }
        }
        
        setMonologue(target.getAttr('id'));
	}
	// Open a door or do a transition
	else if (target.getAttr('category') == 'door') {
		setMonologue(target.getAttr('id'));
        
        var object = objects_json[target.getAttr('object_name')];
        
        if (object.blocked === true)
        	setMonologue(target.getAttr('id'));
        else if (object.state == 'closed') {
        	if (object.locked === true) {
            	object.state = 'locked';
        		stage.get('#' + object.locked_image)[0].show();
            }
            else {
            	object.state = 'open';
                stage.get('#' + object.open_image)[0].show();
            }
        	target.hide();
			current_layer.draw();
        }
        else if (object.state == 'open') {
			// Fading a black screen during the transition
			fade_layer.show();
			fade.play();

			// Animation cycle for proper fading and drawing order
			setTimeout(function() {
				stage.get('#' + current_background)[0].hide();
				target.getParent().hide();
				current_background = object.transition;
				current_layer = stage.get('#object_layer_' + current_background)[0];
                
				stage.get('#' + object.transition)[0].show();
				stage.get('#object_layer_' + object.transition)[0].show();
            	
				fade.reverse();
				stage.draw();
				setTimeout('fade_layer.hide();', 700);
				setMonologue(target.getAttr('id'));
				
				play_music(current_background);
			}, 700);
        }
	}
    // Inventory arrow buttons
    else if (target.getAttr('id') == 'inventory_left_arrow') {
        if (target.getAttr('visible') == true) {
            inventory_index--;
            redrawInventory();
        }
    }
    else if (target.getAttr('id') == 'inventory_right_arrow') {
        if (target.getAttr('visible') == true) {
            inventory_index++;
            redrawInventory();
        }
    }
	// Initiate ending
	else if (target.getAttr('category') == 'ending') {
		play_ending();
	}
}

// Play the hardcoded end sequence and show the correct end screen based on the number of rewards found
function play_ending() {

	var delay = 700;

	// Animation cycle for proper fading and drawing order
	fade_layer.moveToTop();
	stage.get("#black_screen")[0].setSize(stage.getWidth(), stage.getHeight());
	fade_layer.show();
	fade.play();
	
	play_music('outro_layer');
    
	setTimeout(function() {
		stage.get('#' + current_background)[0].hide();
		stage.get('#object_layer_' + current_background)[0].hide();
		inventory_layer.hide();
		
		// Clear inventory except rewards
		for (var i = inventory_layer.children.length-1; i >= 0; i--) {
		    var shape = inventory_layer.children[i];
			if (shape.getAttr('category') != 'reward')
				inventoryRemove(shape);
		}
		
        inventory_index = 0;
		redrawInventory();

		character_layer.hide();
		inventory_bar_layer.hide();
		outro_layer.show();

		fade.reverse();
		stage.draw();
		setTimeout('fade_layer.hide();', 700);
	}, delay);
	delay = delay + 4000;

	setTimeout(function() {
		fade_layer.show();
		fade.play();
		setTimeout(function() {
			outro_layer.hide();
			stage.get('#end_picture_' + rewards)[0].show();
			
			end_layer.moveUp();	
			stage.get('#rewards_text')[0].setText(rewards + stage.get('#rewards_text')[0].getText());
			end_layer.show();
			inventory_bar_layer.show();
			inventory_layer.show();
			character_layer.show();
			stage.draw();
			fade.reverse();
			setTimeout('fade_layer.hide();', 700);
		}, 700);
	}, delay);

}

// Set monologue text
function setMonologue(id, name) {
    if (!name)
        name = 'examine';
        
    // Is there such an ID in JSON?
    var text = texts_json[id];
    if (!text)
        return;
        
    text = text[name];
    
    // Is there such a text?
    if (!text || text.length == 0)
        return;
        
	monologue.setWidth('auto');
	speech_bubble.show();
	monologue.setText(text);
	if (monologue.getWidth() > 524) {
		monologue.setWidth(524);
		monologue.setText(text);
	}

	speech_bubble.setY(stage.getHeight() - 100 - 15 - monologue.getHeight() / 2);

	// Playing the speaking animation
	idle_1.hide();
	speak_1.show();
	speak_1_animation.play();

	text_layer.draw();
	character_layer.draw();

	clearTimeout(monologue_timeout);
	monologue_timeout = setTimeout('stopTalking();', 3000);
}

// Clearing the given text
function clearText(text) {
	text.setText("");

	if (text.getId() == 'monologue') {
		speech_bubble.hide();
	}
	text_layer.draw();
}

// Stop the talking animations
function stopTalking() {
	character_layer.getChildren().each(function(shape, i) {
		shape.hide();
	});
	stage.get("#character_idle_1")[0].show();

	speak_1_animation.reset();
	speak_2_animation.reset();

	character_layer.draw();

}

// Load json from the server
function getJSON(json_file) {
	var request = new XMLHttpRequest();
	request.open("GET", json_file, false);
	request.send(null)
	var json = request.responseText;
	return json;
}

// Setting an image to the stage and scaling it based on relative values if they exist
function createObject(o) {
	window[o.id] = new Image();
	window[o.id].onLoad = function() {
		stage.get('#' + o.id)[0].setImage(window[o.id]);
	}();
	window[o.id].src = o.src;
}

// Adding an item to the inventory
function inventoryAdd(item) {
	item.moveTo(inventory_layer);
	item.clearImageHitRegion();
	item.setScale(1);
	item.setSize(80, 80);
	inventory_items++;
	redrawInventory();
}

// Removing an item from the inventory
function inventoryRemove(item) {
	item.hide();
	item.moveTo(current_layer);
	item.setDraggable(false);
        inventory_items--;
	redrawInventory();
}

// Dragging an item from the inventory
function inventoryDrag(item) {
	item.moveTo(current_layer);
	clearText(monologue);
	stopTalking();
	inventory_layer.draw();
        inventory_items--;
	redrawInventory();
        item.moveToTop();
        current_layer.draw();
}

// Redrawing inventory
function redrawInventory() {
        inventory_layer.getChildren().each(function(shape, i) {
            shape.setAttr('visible', false);
            shape.setDraggable(false);
	});
        
        for(var i = inventory_index; i < Math.min(inventory_index + inventory_max, inventory_items); i++) {
            shape = inventory_layer.getChildren()[i];
            if (shape.getAttr('category') != 'reward') {
                shape.setAttr('category', 'usable');
            }
            shape.setDraggable(true);
            shape.setX(offsetFromLeft + (i - inventory_index) * 100);
            shape.setY(stage.getHeight() - 90);
            shape.setAttr('visible', true);
        }
        
        if(inventory_index > 0) {
            stage.get('#inventory_left_arrow').show();
        } else {
            stage.get('#inventory_left_arrow').hide();
        }
        
        if(inventory_index + inventory_max < inventory_items) {
            stage.get('#inventory_right_arrow').show();
        } else {
            stage.get('#inventory_right_arrow').hide();
        }
        
        inventory_bar_layer.draw();
	inventory_layer.draw();
}

// Delay to be set after each intersection check
function setDelay(delay) {
	delayEnabled = true;
	setTimeout('delayEnabled = false;', delay);
}
