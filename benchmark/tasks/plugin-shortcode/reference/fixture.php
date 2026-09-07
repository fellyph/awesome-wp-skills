<?php
/* Plugin Name: Benchmark Fixture */
add_shortcode('bench_greeting', function ($atts) { $a=shortcode_atts(['name'=>'Visitor'], $atts); return '<span>Hello, '.esc_html($a['name']).'</span>'; });
