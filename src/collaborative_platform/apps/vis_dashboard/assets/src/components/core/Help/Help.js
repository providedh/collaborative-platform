import React from 'react'
import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars

export default function Help (props) {
  return (
    <div id="help" className={'container shadow-lg pt-2 hidden ' + styles.help}>
      <h3>
                PROVIDEDH Visualization Dashboard
        <button type="button" onClick={() => document.getElementById('help').classList.add('hidden')} className="close mt-2 mr-2" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </h3>
      <hr/>
      <div className={styles.overflowContainer}>
        <div>
          <div className="row ml-0 mr-0">
            <h2>Using the dashboard</h2>
          </div>
          <div className="row ml-0 mr-0 flex-column">
            <p className={styles.narrowParagraph}>
              This page allows arranging multiple graphics for displaying data from the project's document,
              which will get updated as the documents in the project change.
              The dashboard app has three main sections:
            </p>
            <ul>
              <li>A top bar where this help menu and the save button are located.</li>
              <li>A left expandable grid workspace where the visualizations are placed.</li>
              <li>A collapsible right menu from where new visualizations are chosen and existing ones are edited.</li>
            </ul>
            <p className={styles.narrowParagraph}>
              All the available graphics are created within the right side panel. Select the type of graphic in
              the top most selector, choose the desired options and hit the <i>Create</i> button. <br/><br/>
              The graphics will be added to the left workspace, where they can be repositioned by dragging from
              the top bar or resized by dragging from the bottom-right corner. <br/><br/>
              Following is a description for each of the provided visualization types:
            </p>
          </div>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h4>Bar chart</h4>
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
                <li className="list-group-item">Number of annotations per document</li>
                <li className="list-group-item">Number of annotations per category</li>
                <li className="list-group-item">Number of annotations per author</li>
                <li className="list-group-item">Entity attributes</li>
                <li className="list-group-item">Most annotated attribute values</li>
                <li className="list-group-item">Type of annotation</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h4>Timeline</h4>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Represent the time span of a document based on its time entities.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                Each horizontal line represents a document, which span accross the dates mentioned in the text.
                These date entities must have the <i>when</i> property correctly set for it to be placed. 
              </p>
              <p>
                Each vertical line represents a date entity, and will be colored based on whether it is filtered
                out (gray) or unfiltered (blue).
              </p>
              <p>
                The timeline can be zoomed in, which will cause any date entity out of sight to be filtered out in
                this and the rest of the visualizations.
              </p>
            </div>
            <div className="col-sm"></div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h4>Map</h4>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Show entities and annotations referring to locations placed within a global map.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                This view allows to see where <i>place</i> entities are located based on their <i>geo</i> property.
                Uncertainty annotations are placed where the entity they refer to would be place.
              </p>
              <p>
                The left globe of the world allows zooming and panning. Whenever zooming or panning is done, the 
                top-right minimap will show a red contour of where the visible area is located.<br/>
                Also, zooming and panning will filter out entities that are not visible within the globe view.
              </p>
            </div>
            <div className="col-sm">
              <h5>Configuration Parameters</h5>
              <ul>
                <li><b>Rendered items</b><br/>
                  Choose wether to have entities or annotations being rendered in the map.
                </li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h4>Pixel Corpus</h4>
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
            <h4>Sunburst</h4>
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
                <li className="list-group-item">Author</li>
                <li className="list-group-item">Type</li>
                <li className="list-group-item">Document</li>
                <li className="list-group-item">Category</li>
                <li className="list-group-item">Attribute</li>
                <li className="list-group-item">Certainty</li>
                <li className="list-group-item">Degree</li>
              </ul>
              <p>Available entity dimensions</p>
              <ul className="list-group ">
                <li className="list-group-item">Text</li>
                <li className="list-group-item">Type</li>
                <li className="list-group-item">Properties</li>
                <li className="list-group-item">Document name</li>
                <li className="list-group-item">Id</li>
              </ul>
            </div>
          </div>
          <hr/>
        </div>
        <div>
          <div className="row ml-0 mr-0">
            <h4>Heatmap</h4>
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
            <h4>Document view</h4>
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
            <h4>Note</h4>
          </div>
          <div className="row ml-0 mr-0">
            <h5><i>Add your findings and thoughts using Markdown notes.</i></h5>
          </div>
          <div className="row mt-2">
            <div className="col-sm">
              <p>
                    This views allows rendering rich text notes by using the Markdown
                    format.
              </p>
            </div>
            <div className="col-sm">
              <p>
                    The Markdown format provides structure and styling using plain text
                    and can be read about here: <a href="https://guides.github.com/features/mastering-markdown/">
                        https://guides.github.com/features/mastering-markdown/
                    </a>.
              </p>
            </div>
            <div className="col-sm">
            </div>
          </div>
          <hr/>
        </div>
      </div>
    </div>
  )
}
