const fs = require('fs');

// Step 1: Read the input JSON file
const fileName = ['dpd_ebts','dpd_i2h','dpd_deconstructor']

const formatDic = (fileName) =>{

const inputFilePath = './' + fileName + '.json'; // Adjust the path as necessary
const inputData = JSON.parse(fs.readFileSync(inputFilePath, 'utf8'));

// Step 2: Transform the JSON structure
const transformedData = Object.keys(inputData).map(key => ({
    entry: key,
    defintion: inputData[key]
}));

// Step 3: Write the transformed JSON to a file
const outputFilePath = '../dictionaries/simple/en/' + fileName + '.json'; // Adjust the path as necessary
fs.writeFileSync(outputFilePath, JSON.stringify(transformedData, null, 2), 'utf8');

console.log('Transformation completed and output written to', outputFilePath);

}

fileName.forEach(fileName => formatDic(fileName))
