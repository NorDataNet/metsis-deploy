<script>
  fetch(<?php echo('"' . $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_plot_query'] . '"');  ?>)
    .then(function (response) {
      return response.json();
    })
    .then(function (item) {
      Bokeh.embed.embed_item(item);
    })
</script>
<div class="row">
  <div class="plot-container">
    <div id="tsplot">

      <!--    The plot appears here.-->
    </div>
  </div>

  <div class="vars-container">
    <div class="fixed-width"><?php print render($form['x_axis']); ?></div>
    <div class="flex-width"><?php print render($form['y_axis']); ?></div>
    <div
      class="plot-submit"><?php print render($form['actions']['submit']); ?></div>
  </div>
</div>
<!-- Render any remaining elements, such as hidden inputs (token, form_id, etc). -->
<?php print drupal_render_children($form); ?>
