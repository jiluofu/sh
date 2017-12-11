package main

import (

    "fmt"
    // "io"
    // "strings"
    "io/ioutil"
    "regexp"
    // "os/exec"
)

var listFile []string //获取文件列表



// 遍历目录
const PATH = "/Users/zhuxu/Documents/sh/go_bili.data"
// const PATH = "/Users/zhuxu/Documents/readlog/"

const WRITEPATH = "/Users/zhuxu/Documents/readlog/log.md"

func main() {

    data, _ := ioutil.ReadFile(PATH)
    // data = string(data)
    // fmt.Println(data)

    re, _ := regexp.Compile(`value='([^']*)'`)
    res := re.FindAllStringSubmatch(string(data), -1)

    re2, _ := regexp.Compile(`>[\d]*、([^']*)</`)
    res2 := re2.FindAllStringSubmatch(string(data), -1)
    
    for i := 0; i < len(res); i ++ {

        url := fmt.Sprintf("https://www.bilibili.com%s", res[i][1]) 
        // fmt.Println(url)
        // fmt.Println(res2[i][1])
        fmt.Println("you-get -o ~/Downloads/ -O 《中国通史》" + res2[i][1] + " " + url)
        // if i == 0 {

            // cmd := exec.Command("/bin/sh", "-c", "you-get -o ~/Downloads/ -O %s " + url)
            // _, err := cmd.Output()
            // if err != nil {
            //     panic(err.Error())
            // }
        // }    
    }



}





