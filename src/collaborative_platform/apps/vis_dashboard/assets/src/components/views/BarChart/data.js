import { useState, useEffect } from 'react'
import * as d3Array from 'd3-array'

export default function useData (dataClient, option, entityType ) {
  const [data, setData] = useState(null)

  if (!Object.hasOwnProperty.call(dataOptions, option)) { return }

  useEffect(() => {
    dataOptions[option](dataClient, setData, entityType)
    return dataClient.clearFiltersAndSubscriptions
  }, [option, entityType])

  return data
}

const dataOptions = {
  entitiesPerDoc,
  entitiesPerType,
  commonEntities,
  annotationsPerDoc,
  annotationsPerCategory,
  annotationsPerAuthor,
  commonAttributeValues,
  annotationAttributes,
  annotationLocus
}

function entitiesPerDoc (dataClient, setData) {
  dataClient.subscribe('entity', ({ all, filtered }) => {
    //console.log('docs', all, filtered)
    setData({
      dimension: 'file_id',
      filterDimension: 'fileId',
      all: d3Array.group(all, x => x.file_id),
      filtered: d3Array.group(filtered, x => x.file_id)
    })
  })
}

function entitiesPerType (dataClient, setData) {
  dataClient.subscribe('entity', ({ all, filtered }) => {
    //console.log(all)
    setData({
      dimension: 'type',
      filterDimension: 'entityType',
      all: d3Array.group(all, x => x.type),
      filtered: d3Array.group(filtered, x => x.type)
    })
  })
}

function commonEntities (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
  alert('The entity type of the annotated piece is not yet exposed')
  setData({
    dimension: 'type',
    filterDimension: 'fileId',
    all: d3Array.group(all, x=>x.file),
    filtered: d3Array.group(filtered, x=>x.file)
  });
  })
}

function annotationsPerDoc (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
    setData({
      dimension: 'file id',
      filterDimension: 'fileId',
      all: d3Array.group(all, x => x.file_id),
      filtered: d3Array.group(filtered, x => x.file_id)
    })
  })
}

function annotationsPerCategory (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
    setData({
      dimension: 'certaintyCategory',
      filterDimension: 'categories',
      all: groupByArrayKeys(all, x => x.categories),
      filtered: groupByArrayKeys(filtered, x => x.categories)
    })
  })
}

function annotationsPerAuthor (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
    setData({
      dimension: 'author',
      filterDimension: 'author',
      all: d3Array.group(all, x => x.resp),
      filtered: d3Array.group(filtered, x => x.resp)
    })
  })
}

function groupByArrayKeys(data, accessor) {
  const joinStr = '[temp]'
  const grouped = d3Array.group(data, d => accessor(d).join(joinStr))
  const remapped = new Map(
    [...(grouped)].map(([strKey, val]) => [strKey.split(joinStr), val])
  )
  return remapped  
}

function commonAttributeValues (dataClient, setData, entity) {
  dataClient.subscribe('entity', ({ all, filtered }) => {
    setData({
      dimension: 'entityAttribute',
      filterDimension: 'entityPropertyKeys',
      all: groupByArrayKeys(all.filter(x => x.type === entity), x => Object.keys(x.properties)),
      filtered: groupByArrayKeys(filtered.filter(x => x.type === entity), x => Object.keys(x.properties))
    })
  })
}

function annotationAttributes (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
    setData({
      dimension: 'attribute',
      filterDimension: 'match',
      all: d3Array.group(all.filter(d => d.match !== null), x => x.match),
      filtered: d3Array.group(filtered.filter(d => d.match !== null), x => x.match)
    })
  })
}

function annotationLocus (dataClient, setData) {
  dataClient.subscribe('certainty', ({ all, filtered }) => {
    setData({
      dimension: 'locus',
      filterDimension: 'locus',
      all: d3Array.group(all, x => x.locus),
      filtered: d3Array.group(filtered, x => x.locus)
    })
  })
}
