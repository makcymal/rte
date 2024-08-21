
// function to format fields for rendering monitoring table. VUE V-for easier works with arrays instead of dictionaries
export function formatHeaderOutput(headerData) {
    let formattedData = {} // new header data formatted to fill the table
    let clusteredFields = [] // contains name of big field (cpu, mem ...)
    let clusteredFieldsSpan = [] // contains column span size for big field (cpu, mem ...)
    let fields = [] // all table fields
    let fieldsDataType = {} // datatypes of all table fields

    let keys = Object.keys(headerData);
    keys.shift()

    for (var key of keys){
        clusteredFields.push(key)
        clusteredFieldsSpan.push(Object.keys(headerData[key]).length)

        fields = fields.concat(Object.keys(headerData[key]))
        fieldsDataType = Object.assign({}, fieldsDataType, headerData[key])
    }

    formattedData['original_data'] = headerData
    formattedData['clustered_fields'] = clusteredFields
    formattedData['clustered_fields_span'] = clusteredFieldsSpan
    formattedData['fields'] = fields
    formattedData['fields_data_type'] = fieldsDataType
    return formattedData
}

// function to format compute nodes data to render in v-for with data of formatted header
export function formatComputeNodeOutput(computeNodesData) {
    let formattedData = {}
    let keys = Object.keys(computeNodesData);
    for (var key of keys){
        formattedData = Object.assign({}, formattedData, computeNodesData[key])
    }
    let node_name = computeNodesData.header.split('!')['2']
    formattedData['name'] = node_name
    return formattedData
}

export function computeAvgTotalOutput(fields, fields_data_type, nodesData) {
    let formattedData = {}
    let avg = {}
    let total = {}
    for (var field of fields){
        let data = 0
        let count = 0
        for (let i = 0; i < nodesData.length; i++){
            if (typeof nodesData[i][field] === "number" || typeof nodesData[i][field] === "bigint"){
                data += nodesData[i][field]
                count++
            }
        }
        if (count > 0 && fields_data_type[field] !== 'hz') {
            avg[field] = Math.round(data / count, 2)
        } else {
            avg[field] = '-'
        }
        if (fields_data_type[field] === "%" || fields_data_type[field] === "hz"){
            total[field] = '-'
        } else {
            total[field] = Math.round(data, 2)
        }
    }
    formattedData['avg'] = avg
    formattedData['total'] = total
    return formattedData

}