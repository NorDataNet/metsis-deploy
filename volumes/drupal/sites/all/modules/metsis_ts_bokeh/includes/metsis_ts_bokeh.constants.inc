<?php

/**
 * The globals must be able to be set form the module admin form
 * Only constants should be set here
 * Constants should have defaults values
 * Constants should be read from the global $metsis_ts_bokeh; if they are
 * defined
 */
global $metsis;

if (isset($metsis['ts_bokeh_init_node'])) {
  define('TS_BOKEH_INIT_NODE', $metsis['ts_bokeh_init_node']);
}
else {
  drupal_set_message('Module is not configured. Visit the module admin page.', 'warning');
}
if (isset($metsis['ts_bokeh_init_node'])) {
  define('TS_BOKEH_PLOT_NODE', $metsis['ts_bokeh_plot_node']);
}
else {
  drupal_set_message('Module is not configured. Visit the module admin page.', 'warning');
}
//if (isset($metsis['ts_bokeh_plot_service'])) {
//  define('TS_BOKEH_PLOT_SERVICE', $metsis['ts_bokeh_plot_service']);
//}
//else {
//  drupal_set_message('Module is not configured. Visit the module admin page.', 'warning');
//}
