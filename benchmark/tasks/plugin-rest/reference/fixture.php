<?php
/* Plugin Name: Benchmark Fixture */
add_action('rest_api_init',function(){register_rest_route('bench/v1','/status',['methods'=>'GET','callback'=>function(){return ['ready'=>true];},'permission_callback'=>function(){return current_user_can('manage_options');}]);});
