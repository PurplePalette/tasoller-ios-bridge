const PTFakeMetaTouch = ObjC.classes.MyPTFakeMetaTouch;
const simulateTouch = (touchType: number, identifier: number, x: number, y: number) => {
    PTFakeMetaTouch.simulateTouch_x_y_identifier_(touchType, x, y, identifier+10);
};
const recvTouch = () => {
    recv("in", (msg) => {
        console.log(msg.ttype, msg.tid, msg.x, msg.y);
        simulateTouch(msg.ttype, msg.tid, msg.x, msg.y);
        recvTouch();
    });
};
recvTouch();