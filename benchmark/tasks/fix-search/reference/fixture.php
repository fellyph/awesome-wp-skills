<?php
/* Plugin Name: Benchmark Fixture */
function bench_search($title){global $wpdb; $like='%'.$wpdb->esc_like($title).'%'; return array_map('intval',$wpdb->get_col($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_status='publish' AND post_type='post' AND post_title LIKE %s ORDER BY ID",$like)));}
