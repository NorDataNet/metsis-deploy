<?php

/**
 * @param $key
 * @param null $value
 *
 * @return mixed
 */

//function lists_session($key, $value = NULL) {
//  /**
//   * save variable in session: lists_session('s_key', 'value');
//   * retrieve the value: $myVar = lists_session('s_key')
//   */
//  static $storage;
//  if ($value) {
//    $storage[$key] = $value;
//    $_SESSION['lists'][$key] = $value;
//  }
//  else {
//    if (empty($storage[$key]) && isset($_SESSION['lists'][$key])) {
//      $storage[$key] = $_SESSION['lists'][$key];
//    }
//  }
//  return $storage[$key];
//}

/**
 * @param $uri
 *
 * @return mixed
 */
function adc_get_ts_bokeh_plot_vars($uri) {
  $request = drupal_http_request($uri);
  /**
   * TODO - validate the data URI - issue waring if no data is found
   */
  if ($request->code != 200) {
    drupal_set_message("Service call did not succeed. Ensure that the following URL is correct.", 'error');
    drupal_set_message($uri, 'error');
    /**
     * TODO: 'ts_bokeh_init' must be parametrized and set in the module admin interface.
     */
    drupal_goto(TS_BOKEH_INIT_NODE);
  }
  $json_response = drupal_json_decode($request->data);
  return ($json_response);
}

/**
 * @param string $uri
 *
 * @return mixed
 */
//function adc_get_ts_bokeh_plot($uri = TS_BOKEH_PLOT_SERVICE . '?get=plot&resource_url=http://hyrax:8080/opendap/SN99938.nc&variable=relative_humidity') {
//  $request = drupal_http_request($uri);
//  $json_response = drupal_json_decode($request->data);
//  return ($json_response);
//}

/**
 * @return array
 */
function adc_get_ts_bokeh_plot_y_vars() {
  $ts_bokeh_plot_vars = adc_get_ts_bokeh_plot_vars($_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_data_uri']);
  $y_vars = $ts_bokeh_plot_vars['y_axis'];
  ksort($y_vars);
  $hy_vars = [];
  foreach ($y_vars as $yv) {
    $hy_vars[$yv] = $yv;
  }
  return ($hy_vars);

}

/**
 * @param $form_state
 *
 * @return string
 */
function adc_get_ts_bokeh_plot_query($form_state) {
  $sra = explode("=param", $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_data_uri']);
  return ($sra[0] . '=plot' . $sra[1] . '&variable=' . $form_state['values']['y_axis']);
}
