package main

import (

    "fmt"
    // "io"
    // "strings"
    "io/ioutil"
    "regexp"
    "os/exec"
)

var listFile []string //获取文件列表



// 遍历目录
const PATH = "/Users/zhuxu/Documents/sh/go_peppa.data.chs"
// const PATH = "/Users/zhuxu/Documents/readlog/"

const WRITEPATH = "/Users/zhuxu/Documents/readlog/log.md"

func main() {

    data, _ := ioutil.ReadFile(PATH)
    // data = string(data)
    // fmt.Println(data)

    re, _ := regexp.Compile(`data-vid="([^"]*)"`)
    res := re.FindAllStringSubmatch(string(data), -1)
    
    for i := 0; i < len(res); i ++ {

        url := fmt.Sprintf("http://www.le.com/ptv/vplay/%s.html", res[i][1]) 
        // fmt.Println(url)
        // if i == 0 {

            cmd := exec.Command("/bin/sh", "-c", "you-get -o ~/Downloads/ " + url)
            _, err := cmd.Output()
            if err != nil {
                panic(err.Error())
            }
        // }    
    }



}





