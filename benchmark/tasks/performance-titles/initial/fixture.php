<?php
/* Plugin Name: Benchmark Fixture */
function bench_titles($ids){global $wpdb;$out=[];foreach($ids as $id){$t=$wpdb->get_var($wpdb->prepare("SELECT post_title FROM {$wpdb->posts} WHERE ID=%d AND post_status='publish'",$id));if($t!==null)$out[]=$t;}return $out;}
