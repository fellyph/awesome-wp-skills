<?php
/* Plugin Name: Benchmark Fixture */
function bench_titles($ids){if(!$ids)return []; $posts=get_posts(['post__in'=>array_unique($ids),'posts_per_page'=>count(array_unique($ids)),'post_status'=>'publish','update_post_meta_cache'=>false,'update_post_term_cache'=>false]);$map=[];foreach($posts as $p)$map[$p->ID]=$p->post_title;$out=[];foreach($ids as $id)if(isset($map[$id]))$out[]=$map[$id];return $out;}
