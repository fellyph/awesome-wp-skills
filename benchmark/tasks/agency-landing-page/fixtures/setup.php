<?php require '/wordpress/wp-load.php';
$p=WP_Block_Patterns_Registry::get_instance()->get_registered('benchmark-fixture/landing');
$content=$p['content']??'';
$id=(int)get_option('page_on_front');
$post=['post_title'=>'Northline','post_type'=>'page','post_status'=>'publish','post_content'=>$content];
if($id){$post['ID']=$id;} $id=wp_insert_post($post);
update_option('page_on_front',$id);update_option('show_on_front','page');
update_option('blogname','Northline');update_option('blogdescription','Independent digital studio');
update_option('benchmark_submissions',[]);echo $id;
