import React from 'react'
import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars

export default function Help (props) {
  return (
    <div id="help" className={'container shadow-lg pt-2 hidden ' + styles.help}>
      <h3>
                Views in the PROVIDEDH Visualization Dashboard
        <button type="button" onClick={() => document.getElementById('help').classList.add('hidden')} className="close mt-2 mr-2" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </h3>
      <hr/>
      <div className={styles.overflowContainer}>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Bar chart</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display distributions by encoding the information with bars.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
              </p>
              <p>
                                Hovering over the bars will display a tooltip with the bar information. If
                                the bar represents a document, this will be focused (will be shown in the
                                Document View component).
              </p>
              <p>
                                Filtering can be done by clicking on the bars. Once a bar has been selected,
                                add more to the selection by clicking on more.<br/>
                                Undo the filtering by clicking again on a selected bar.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Bar direction</b><br/>
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                </li>
                <li><b>Dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering
                                    done through other views.
                </li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Number of entities per document</li>
                <li className="list-group-item">Number of entities per type</li>
                <li className="list-group-item">Most annotated entities</li>
                <li className="list-group-item">Number of annotations per document</li>
                <li className="list-group-item">Number of annotations per category</li>
                <li className="list-group-item">Number of annotations per author</li>
                <li className="list-group-item">Frequency for an attribute&apos;s values</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Pixel Corpus</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Show how the specific entities and annotations are distributed in the collection.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Rows representing each document show the different entities and annotations. Each row
                                can be hovered to focus the document (show it in the Document View component);
              </p>
              <p>
                                Sorting the documents allow to put special attention in the desired documents, and
                                discover trends in the data; such as periodics authors when sorting the documents
                                by date edition, and coloring the entities by their author.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Source</b><br/>
                                    Choose wether to have entities or annotations being represented in the view.
                </li>
                <li><b>Sort documents by</b><br/>
                                    Sort documents to better see what the state is for more recent,
                                    larger, or most contributed documents is.
                </li>
                <li><b>Color certainty by</b><br/>
                                    Choose what will be shown in the complimentary view. This second
                                    representation of the corpus allows to see how the category, source,
                                    entity type, or other aspects are annotated along the document collection.
                </li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Eligible options for document sorting</p>
              <ul className="list-group ">
                <li className="list-group-item">Most self contributed first</li>
                <li className="list-group-item">Least self contributed first</li>
                <li className="list-group-item">Last edited first</li>
                <li className="list-group-item">Last edited last</li>
                <li className="list-group-item">Higher entity count first</li>
                <li className="list-group-item">Higher entity count last</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Heatmap</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display distributions encoding the information with bars.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Tile layout</b><br/>
                                    Toggle between a regular, split, or tile layout for the grid; which
                                    allows to remove redundant information for the eligible options.
                </li>
                <li><b>Color scale</b><br/>
                                    Choose between a set of available color schemes for encoding the
                                    selected dimension.
                </li>
                <li><b>Range scale</b><br/>
                                    Choose what type of transformation will be applied to the data, allowing
                                    the least or most represented entries to be more visible.
                </li>
                <li><b>Source</b><br/>
                                    Choose wether to use entities or annotations in the visualization.
                </li>
                <li><b>Axis 1 and 2</b><br/>
                                    Choose what different dimension are used to map data in the visualization,
                                    being Axis1 the dimension used for the rows, and Axis2 for the columns;
                </li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available certainty dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Id</li>
                <li className="list-group-item">Tag</li>
                <li className="list-group-item">type</li>
                <li className="list-group-item">Text</li>
              </ul>
              <p>Available entity dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Id</li>
                <li className="list-group-item">Text</li>
                <li className="list-group-item">Tag</li>
                <li className="list-group-item">Document name</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Document view</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display the contents of a project&apos;s document.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                This widget renders the contents of a document using the current taxonomy configuration,
                                and allows launching to the <i>Annotator</i> with the selected document.
              </p>
              <p>
                                The shown document can be set manually or left to be sync with the views; then, hovering
                                elements representing a document will render it in this view.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Show entities</b><br/>
                                    If selected, the entities will be shown using the same configuration as the annotator.
                </li>
                <li><b>Show certainty</b><br/>
                                    If selected, the annotations will be shown using the same configuration as the annotator.
                </li>
                <li><b>Sync with views</b><br/>
                                    If selected, the document shown in this view will be the focused document; changed
                                    by interacting (clicking) with the rest of views.
                </li>
                <li><b>Document</b><br/>
                  <em>Available when the view is not synched</em>, allows to choose what document is shown.
                                    When the document is selected manually, interacting with other views will not affect it.
                </li>
              </ul>
            </div>
            <div className="col-sm">
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Chord Diagram</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Create and display hierarchical distributions using a radial treemap.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                The sunburst view allows to see how the data is distributed along the corpus.
                                By creating hierarchies based on the entity and annotation attributes trends,
                                outliers and author activity can be shown.
              </p>
              <p>
                                Click interactions are used filter data, leaving the rest of it more space to
                                be rendered; Thus, revealing least represented cases.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Source</b><br/>
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                </li>
                <li><b>Number of levels</b><br/>
                                    Each level added will be another ring in the sunburst visualization.
                                    A higher amount of levels allow for a finer classification, but can
                                    difficult interpreting it.
                </li>
                <li><b>Levels 1 to n</b><br/>
                                    Select what dimension will be used to define the hierarchy at that level.
                                    Levels 1 to n go represent the inner to the outer rings of the visualization.
                </li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available certainty dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Category</li>
                <li className="list-group-item">Author</li>
                <li className="list-group-item">Certainty</li>
                <li className="list-group-item">Degree</li>
                <li className="list-group-item">Attribute</li>
                <li className="list-group-item">Document</li>
              </ul>
              <p>Available entity dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Type</li>
                <li className="list-group-item">Text</li>
                <li className="list-group-item">Id</li>
                <li className="list-group-item">Document name</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div className="d-none">
          <div className="row ml-0 mr-0">
            <h2>Map</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display distributions encoding the information with bars.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>barDirection</b><br/>
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                </li>
                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering
                                    done through other views.
                </li>
                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Number of entities per document</li>
                <li className="list-group-item">Number of entities per type</li>
                <li className="list-group-item">Number of annotations per document</li>
                <li className="list-group-item">Number of annotations per category</li>
                <li className="list-group-item">Frequency for an attribute&apos;s values</li>
                <li className="list-group-item">Frequency for most common attribute values</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div className="d-none">
          <div className="row ml-0 mr-0">
            <h2>Violin Plot</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display distributions encoding the information with bars.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>barDirection</b><br/>
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                </li>
                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering
                                    done through other views.
                </li>
                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Number of entities per document</li>
                <li className="list-group-item">Number of entities per type</li>
                <li className="list-group-item">Number of annotations per document</li>
                <li className="list-group-item">Number of annotations per category</li>
                <li className="list-group-item">Frequency for an attribute&apos;s values</li>
                <li className="list-group-item">Frequency for most common attribute values</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div className="d-none">
          <div className="row ml-0 mr-0">
            <h2>Timeline</h2>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Display distributions encoding the information with bars.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>barDirection</b><br/>
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                </li>
                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering
                                    done through other views.
                </li>
                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
              </ul>
            </div>
            <div className="col-sm">
              <p>Available dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Number of entities per document</li>
                <li className="list-group-item">Number of entities per type</li>
                <li className="list-group-item">Number of annotations per document</li>
                <li className="list-group-item">Number of annotations per category</li>
                <li className="list-group-item">Frequency for an attribute&apos;s values</li>
                <li className="list-group-item">Frequency for most common attribute values</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
      </div>
    </div>
  )
}
