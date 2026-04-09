<?php

$router->get('/api/health', function () {
    echo json_encode(['ok' => true]);
});

$router->post('/api/messages', [MessageController::class, 'store']);
