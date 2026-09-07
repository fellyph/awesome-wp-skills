<?php
/* Plugin Name: Benchmark Fixture */
function bench_search($title){global $wpdb;return array_map('intval',$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_status='publish' AND post_type='post' AND post_title LIKE '%$title%' ORDER BY ID"));}
