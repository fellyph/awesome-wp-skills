<?php
/* Plugin Name: Benchmark Fixture */
function bench_ratings($ids){$out=[];foreach($ids as $id)$out[$id]=get_post_meta($id,'bench_rating',true);return $out;}
