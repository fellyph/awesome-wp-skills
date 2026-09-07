<?php
/* Plugin Name: Benchmark Fixture */
function bench_published_count(){global $wpdb;return (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish'");}
