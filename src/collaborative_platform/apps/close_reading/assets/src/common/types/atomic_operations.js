
export const AtomicActionType = {add: 'add', modify:'modify', delete: 'delete'}
export const AtomicActionTarget = {text: 'text', entity: 'entity', certainty: 'certainty'}
export const AtomicActionObject = {
    tag: 'tag', 
    referece: 'reference', 
    property: 'property', 
    unification: 'unification',
    certainty: 'certainty'
}

export function AtomicAction (type, target, object){
    const action = actions?.[type]?.[target]?.[object]
    return action
}

const actions = {
    text: {
        add:{
            tag: (start, end)=>({
                "element_type": "tag",
                "method": "POST",
                "parameters": {
                    "start_pos": start,
                    "end_pos": end
                }
            })
        },
        modify: {
            tag: (id, oldStart, oldEnd, newStart, newEnd)=>({
                "element_type": "tag",
                "method": "PUT",
                "edited_element_id": id,
                "parameters": {
                    "start_pos": oldStart,
                    "end_pos": oldEnd,
                    "new_start_pos": newStart,
                    "new_end_pos": newEnd
                }
            })
        },
        delete: {
            tag: (id)=>({
                "element_type": "tag",
                "method": "DELETE",
                "edited_element_id": id
            })
        }
    },
    entity: {
        add:{
            reference: ()=>({}),
            property: (id, properties)=>({
                "element_type": "entity_property",
                "method": "POST",
                "edited_element_id": id,
                "parameters": properties
            }),
            unification: ()=>({})
        },
        modify: {
            reference: ()=>({}),
            property: ()=>({}),
            unification: ()=>({})
        },
        delete: {
            reference: ()=>({}),
            property: (id, property)=>({
                "element_type": "entity_property",
                "method": "DELETE",
                "edited_element_id": id,
                "old_element_id": property
            }),
            unification: ()=>({})
        }
    },
    certainty: {
        add:{
            certainty: (target, locus, categories, certainty, assertedValue, description)=>({
                "element_type": "certainty",
                "method": "POST",
                "new_element_id": target,
                "parameters": {
                    "categories": categories,
                    "locus": "value",
                    "certainty": certainty,
                    "asserted_value": assertedValue,
                    "description": description
                }
            })
        },
        modify: {
            certainty: (id, attributeName, attributeValue)=>({
                "element_type": "certainty",
                "method": "PUT",
                "edited_element_id": id,
                "old_element_id": attributeName,
                "parameters": {[attributeName]: attributeValue}
            })
        },
        delete: {
            certainty: (id)=>({
                "element_type": "certainty",
                "method": "DELETE",
                "edited_element_id": id
            })
        }
    }
}
